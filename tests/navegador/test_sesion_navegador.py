"""Fase 8 del plan 001, historia 5: terminar la sesión en un navegador real (T-001-81).

Pruebas P-001-90, P-001-93 y P-001-94 y la parte de navegador de P-001-92, con la marca
`navegador`. Corren aparte de las demás (plan 001, R-8): necesitan un navegador de Playwright
(`python -m playwright install chromium`, que autoriza Jairo, R-7, o el canal del sistema con
`--browser-channel msedge`) y la capa web completa de la Fase 8 (T-001-82 a T-001-85).
Se escribieron antes que ella y fallaron mientras no existió.

Un servidor Uvicorn real, solo en `127.0.0.1`, sirve `app.servidor.crear_app` con el reloj inyectado
(`tests.ayudas_web.Reloj`), uno por prueba. El tiempo de la página se simula con la API de reloj de
Playwright (`page.clock`); el del servidor, con el `Reloj` inyectado. Los dos son independientes:
cada prueba avanza el que necesita. Los archivos se entregan al navegador desde la memoria.

Esperados escritos a mano a partir de `docs/interfaz/flujos.md` §2 (E7, E8, E9) y §3 (F-001-5) y de
ADR-003 (puntos 5 y 9). Ninguno sale de ejecutar el código bajo prueba.

`[NEEDS CLARIFICATION: las plantillas de E7 no fijan su rol ni su marca; las pruebas buscan el aviso
por su texto y el botón por su nombre accesible «Seguir con la sesión».]`
"""

import logging
import time
import urllib.request
from collections.abc import Callable, Iterator
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

import pytest
from playwright.sync_api import Page, expect

from tests.ayudas_web import (
    CABECERA_SESION_FIJA,
    E7_AVISO,
    E7_BOTON,
    E8_DESCARTE,
    E8_INACTIVIDAD,
    E9_RECUPERANDO,
    ETIQUETA_ARCHIVO,
    MIME_XLSX,
    RastrosEnDisco,
    Reloj,
    cabecera_esperada,
    crear_app,
    fixture,
    hay_resultados,
    servidor_real,
    texto_de_registros,
    texto_visible,
)
from tests.constructor import MARCADORES_CELDAS, NOMBRE_CON_MARCADOR

pytestmark = pytest.mark.navegador

BASE = "base_valida.xlsx"
CLAVE_FICHA = "egm-sesion"
MINUTO_MS = 60_000
INICIO_SIMULADO = datetime(2026, 11, 25, 9, 30)


# --- Servidor y páginas -----------------------------------------------------------------------


@dataclass
class Servidor:
    """Un servidor real, su reloj inyectado y el almacén de sesiones de su aplicación."""

    url: str
    reloj: Reloj
    almacen: Any

    def purgar(self) -> int:
        return int(self.almacen.purgar_vencidas(self.reloj()))


@pytest.fixture
def servidor() -> Iterator[Servidor]:
    """Un servidor Uvicorn real en `127.0.0.1`, en un puerto libre, sin registro de accesos."""
    reloj = Reloj()
    app = crear_app(reloj=reloj)
    with servidor_real(app) as url:
        yield Servidor(url, reloj, app.state.servicios.almacen)


@dataclass
class Pestana:
    """Una pestaña con lo que hizo mientras estuvo abierta: peticiones (método, ruta) y consola."""

    pagina: Page
    url: str
    peticiones: list[tuple[str, str]] = field(default_factory=list)
    consola: list[tuple[str, str]] = field(default_factory=list)

    def latidos(self) -> int:
        return sum(1 for m, r in self.peticiones if m == "POST" and r == "/sesion/latido")

    def avisos_de_cierre(self) -> int:
        return sum(1 for m, r in self.peticiones if m == "POST" and r == "/sesion/cierre")


@pytest.fixture
def abrir_pestana(browser: Any, servidor: Servidor) -> Iterator[Callable[..., Pestana]]:
    """Fábrica de pestañas, cada una en su propio contexto (sin almacenamiento compartido)."""
    contextos: list[Any] = []

    def abrir(simulado: bool = False, contexto: Any = None) -> Pestana:
        if contexto is None:
            contexto = browser.new_context(
                viewport={"width": 1280, "height": 900}, color_scheme="light", locale="es-CO"
            )
            contextos.append(contexto)
        pagina = contexto.new_page()
        if simulado:
            pagina.clock.install(time=INICIO_SIMULADO)
        pestana = Pestana(pagina, servidor.url)

        def registrar(peticion: Any) -> None:
            ruta = peticion.url.removeprefix(servidor.url)
            pestana.peticiones.append((peticion.method, ruta))

        pagina.on("request", registrar)
        pagina.on("console", lambda mensaje: pestana.consola.append((mensaje.type, mensaje.text)))
        pagina.on("pageerror", lambda error: pestana.consola.append(("pageerror", str(error))))
        return pestana

    yield abrir
    for contexto in contextos:
        contexto.close()


def _ir_a_inicio(pestana: Pestana) -> None:
    pestana.pagina.goto(pestana.url)
    expect(
        pestana.pagina.get_by_role("heading", name="Cargue la matriz bibliográfica")
    ).to_be_visible()


def _cargar(pestana: Pestana, nombre: str = BASE, contenido: bytes | None = None) -> None:
    pagina = pestana.pagina
    pagina.get_by_label(ETIQUETA_ARCHIVO).set_input_files(
        files=[
            {
                "name": nombre,
                "mimeType": MIME_XLSX,
                "buffer": contenido if contenido is not None else fixture(nombre),
            }
        ]
    )
    pagina.get_by_role("button", name="Cargar la matriz").click()


def _cargar_y_ver(pestana: Pestana, nombre: str = BASE, n_documentos: int = 5) -> None:
    _cargar(pestana, nombre)
    _ver_cabecera(pestana, nombre, n_documentos)


def _ver_cabecera(pestana: Pestana, nombre: str, n_documentos: int) -> None:
    expect(pestana.pagina.locator("#cabecera-corrida .corte")).to_have_text(
        cabecera_esperada(nombre, n_documentos)
    )


def _ficha_de_la_pestana(pestana: Pestana) -> str | None:
    valor = pestana.pagina.evaluate(f"window.sessionStorage.getItem('{CLAVE_FICHA}')")
    return str(valor) if valor else None


def _esperar(condicion: Callable[[], bool], segundos: float = 5.0) -> bool:
    plazo = time.monotonic() + segundos
    while time.monotonic() < plazo:
        if condicion():
            return True
        time.sleep(0.02)
    return condicion()


def _esperar_actividad_en_el_servidor(servidor: Servidor, ficha: str) -> None:
    """Espera a que el servidor haya contado una actividad a la hora que marca su reloj."""
    assert _esperar(
        lambda: (
            (sesion := servidor.almacen.obtener(ficha)) is not None
            and sesion.ultima_actividad == servidor.reloj()
        )
    )


def _asentar(segundos: float = 0.4) -> None:
    """Una espera real corta, para comprobar que NO llega una petición."""
    time.sleep(segundos)


def _avanzar(pestana: Pestana, milisegundos: int) -> None:
    """Hace pasar tiempo simulado en la página, disparando sus temporizadores."""
    pestana.pagina.clock.run_for(milisegundos)


def _en_silencio(pestana: Pestana) -> None:
    """Deja pasar más de un minuto simulado sin interacción y vacía la cuenta de latidos."""
    _avanzar(pestana, 61 * 1000)
    _asentar()
    _avanzar(pestana, 61 * 1000)
    _asentar()
    pestana.peticiones.clear()


def _pedir(url: str, ficha: str | None, ruta: str) -> str:
    """Una petición `GET` desde Python, con la ficha en su cabecera (sin proxy)."""
    peticion = urllib.request.Request(url + ruta)
    if ficha:
        peticion.add_header("X-EGM-Sesion", ficha)
    abridor = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with abridor.open(peticion, timeout=10) as respuesta:
        return str(respuesta.read().decode("utf-8"))


# --- P-001-90: cerrar la pestaña y recargar ---------------------------------------------------


def _cerrar_la_pestana(pestana: Pestana) -> None:
    pestana.pagina.close(run_before_unload=True)


def _esperar_el_aviso_de_cierre(servidor: Servidor) -> int:
    """Hace pasar 11 s en el servidor hasta que su purga borre la sesión (el aviso ya llegó)."""
    borradas = 0
    plazo = time.monotonic() + 8
    while time.monotonic() < plazo and borradas == 0:
        servidor.reloj.avanzar(seconds=11)
        borradas = servidor.purgar()
        if borradas == 0:
            time.sleep(0.1)
    return borradas


def test_p_001_90_cerrar_la_pestana_y_abrir_otra_muestra_la_carga_sin_cifras_y_borra_la_sesion(
    abrir_pestana: Callable[..., Pestana], servidor: Servidor
) -> None:
    """P-001-90 · US-001-5.2, ADR-003 punto 9: V0 sin cifras; a los 10 s no queda la sesión."""
    primera = abrir_pestana()
    _ir_a_inicio(primera)
    _cargar_y_ver(primera)
    ficha = _ficha_de_la_pestana(primera)
    assert ficha
    assert servidor.almacen.cantidad() == 1

    contexto = primera.pagina.context
    _cerrar_la_pestana(primera)
    segunda = abrir_pestana(contexto=contexto)
    _ir_a_inicio(segunda)

    # V0 sin mensaje y sin cifras: la ficha desapareció con la pestaña (almacenamiento propio).
    texto = texto_visible(segunda.pagina.content())
    assert not hay_resultados(texto)
    assert E8_DESCARTE not in texto
    assert E8_INACTIVIDAD not in texto
    assert _ficha_de_la_pestana(segunda) is None
    assert segunda.pagina.locator("#cabecera-corrida .corte").count() == 0

    # Pasados los 10 s de gracia, el servidor ya no tiene la sesión.
    assert _esperar_el_aviso_de_cierre(servidor) == 1
    assert servidor.almacen.cantidad() == 0
    assert servidor.almacen.obtener(ficha) is None
    ya_no = texto_visible(_pedir(servidor.url, ficha, "/vista/resultado"))
    assert not hay_resultados(ya_no)


def test_p_001_90_recargar_antes_de_10_segundos_conserva_la_sesion_y_muestra_e9(
    abrir_pestana: Callable[..., Pestana], servidor: Servidor
) -> None:
    """P-001-90 · US-001-5.2, ADR-003 punto 9: la recarga trae la ficha y la sesión sigue (E9)."""
    pestana = abrir_pestana()
    _ir_a_inicio(pestana)
    _cargar_y_ver(pestana)
    pagina = pestana.pagina
    ficha = _ficha_de_la_pestana(pestana)

    # Se retiene la petición del resultado para ver E9 mientras la sesión se recupera.
    retenidas: list[Any] = []
    pagina.route("**/vista/resultado", lambda ruta: retenidas.append(ruta))
    pagina.reload()
    expect(pagina.get_by_text(E9_RECUPERANDO)).to_be_visible()
    assert _esperar(lambda: len(retenidas) == 1)
    servidor.reloj.avanzar(seconds=5)
    retenidas[0].continue_()
    pagina.unroute("**/vista/resultado")

    _ver_cabecera(pestana, BASE, 5)
    assert _ficha_de_la_pestana(pestana) == ficha
    # El aviso de cierre de la página que se recargó no la borra: la ficha volvió dentro del plazo.
    servidor.reloj.avanzar(seconds=30)
    assert servidor.purgar() == 0
    assert servidor.almacen.cantidad() == 1


def test_p_001_90_sin_ficha_en_la_pestana_no_hay_recuperacion_ni_mensaje(
    abrir_pestana: Callable[..., Pestana],
) -> None:
    """P-001-90 · US-001-5.2, flujos.md E9: sin ficha, la vista de carga sin mensaje."""
    pestana = abrir_pestana()
    _ir_a_inicio(pestana)

    expect(pestana.pagina.get_by_text(E9_RECUPERANDO)).not_to_be_visible()
    assert ("GET", "/vista/resultado") not in pestana.peticiones


def test_p_001_90_cambiar_de_pestana_no_avisa_el_cierre(
    abrir_pestana: Callable[..., Pestana], servidor: Servidor
) -> None:
    """P-001-90 · ADR-003 punto 9: ocultar la pestaña sin cerrarla no termina la sesión."""
    pestana = abrir_pestana()
    _ir_a_inicio(pestana)
    _cargar_y_ver(pestana)
    otra = abrir_pestana(contexto=pestana.pagina.context)
    otra.pagina.goto(otra.url)
    otra.pagina.bring_to_front()
    pestana.pagina.bring_to_front()
    _asentar()

    assert pestana.avisos_de_cierre() == 0
    servidor.reloj.avanzar(seconds=30)
    assert servidor.almacen.obtener(_ficha_de_la_pestana(pestana) or "") is not None


# --- P-001-93: aviso de inactividad (E7) ------------------------------------------------------


def test_p_001_93_e7_aparece_a_los_43_minutos_y_seguir_con_la_sesion_reinicia_la_cuenta(
    abrir_pestana: Callable[..., Pestana],
) -> None:
    """P-001-93 · NFR-000-04 (WCAG 2.2.1), NFR-000-17: E7 a los 43 min con su botón."""
    pestana = abrir_pestana(simulado=True)
    _ir_a_inicio(pestana)
    _cargar_y_ver(pestana)
    pagina = pestana.pagina
    aviso = pagina.get_by_text(E7_AVISO)
    boton = pagina.get_by_role("button", name=E7_BOTON)

    # El último latido de la carga sale al cumplirse su minuto; desde él se cuentan los 43.
    _en_silencio(pestana)
    _avanzar(pestana, 40 * MINUTO_MS)
    expect(aviso).not_to_be_visible()
    _avanzar(pestana, 2 * MINUTO_MS)  # pasan los 43 minutos desde el último contacto
    expect(aviso).to_be_visible()
    expect(boton).to_be_visible()
    expect(pagina.locator("#cabecera-corrida .corte")).to_be_visible()  # la vista en curso sigue

    # Se activa el botón sin mover el puntero (como lo haría un lector de pantalla): con el mouse,
    # el primer movimiento hacia el botón ya cuenta como actividad y retira el aviso.
    boton.dispatch_event("click")
    expect(aviso).not_to_be_visible()
    # Con la cuenta reiniciada, los 45 minutos de la cuenta anterior pasan sin que termine nada.
    _avanzar(pestana, 3 * MINUTO_MS)
    expect(aviso).not_to_be_visible()
    _ver_cabecera(pestana, BASE, 5)
    assert pagina.get_by_text(E8_INACTIVIDAD).count() == 0
    # Y E7 vuelve a los 43 minutos de la nueva cuenta.
    _avanzar(pestana, 41 * MINUTO_MS)
    expect(aviso).to_be_visible()


@pytest.mark.parametrize("interaccion", ["teclado", "puntero"])
def test_p_001_93_otra_interaccion_tambien_reinicia_la_cuenta_y_retira_e7(
    abrir_pestana: Callable[..., Pestana], interaccion: str
) -> None:
    """P-001-93 · NFR-000-04, NFR-000-17: cualquier interacción cuenta, no solo el botón."""
    pestana = abrir_pestana(simulado=True)
    _ir_a_inicio(pestana)
    _cargar_y_ver(pestana)
    pagina = pestana.pagina
    aviso = pagina.get_by_text(E7_AVISO)

    _en_silencio(pestana)
    _avanzar(pestana, 43 * MINUTO_MS)
    expect(aviso).to_be_visible()
    if interaccion == "teclado":
        pagina.keyboard.press("Shift")
    else:
        pagina.mouse.move(300, 300)
    expect(aviso).not_to_be_visible()
    _avanzar(pestana, 2 * MINUTO_MS)
    _ver_cabecera(pestana, BASE, 5)
    assert pagina.get_by_text(E8_INACTIVIDAD).count() == 0


def test_p_001_93_e7_se_anuncia_sin_quitar_el_foco_de_donde_estaba(
    abrir_pestana: Callable[..., Pestana],
) -> None:
    """P-001-93 · NFR-000-04 (WCAG 2.2.1, 4.1.3): el aviso se anuncia y no roba el foco."""
    pestana = abrir_pestana(simulado=True)
    _ir_a_inicio(pestana)
    _cargar_y_ver(pestana)
    pagina = pestana.pagina
    enlace = pagina.get_by_role("link", name="Cargar otro archivo")
    enlace.focus()

    _en_silencio(pestana)
    _avanzar(pestana, 43 * MINUTO_MS)
    aviso = pagina.get_by_text(E7_AVISO)
    expect(aviso).to_be_visible()
    # Es una región de alerta: el lector de pantalla lo lee sin que la persona lo busque.
    anunciado = pagina.locator(
        "[role='alert'], [role='status'], [aria-live='assertive'], [aria-live='polite']"
    ).filter(has_text=E7_AVISO)
    expect(anunciado).to_have_count(1)
    assert pagina.evaluate("document.activeElement.textContent.trim()") == "Cargar otro archivo"


def test_p_001_93_a_los_45_minutos_sin_actividad_aparece_e8_de_inactividad(
    abrir_pestana: Callable[..., Pestana], servidor: Servidor
) -> None:
    """P-001-93 · US-001-5.3, NFR-000-17: E8 a los 45 minutos, sin cifras y sin ficha."""
    pestana = abrir_pestana(simulado=True)
    _ir_a_inicio(pestana)
    _cargar_y_ver(pestana)
    pagina = pestana.pagina

    _en_silencio(pestana)
    servidor.reloj.avanzar(minutes=45)
    _avanzar(pestana, 45 * MINUTO_MS)

    expect(pagina.get_by_text(E8_INACTIVIDAD)).to_be_visible()
    expect(pagina.get_by_role("heading", name="Cargue la matriz bibliográfica")).to_be_visible()
    assert pagina.locator("#cabecera-corrida .corte").count() == 0
    assert not hay_resultados(texto_visible(pagina.content()))
    assert _esperar(lambda: _ficha_de_la_pestana(pestana) is None)
    expect(pagina.get_by_text(E7_AVISO)).not_to_be_visible()


def test_p_001_93_la_cabecera_trae_el_texto_fijo_de_la_sesion_y_el_boton_de_descartar(
    abrir_pestana: Callable[..., Pestana],
) -> None:
    """P-001-93 · FR-001-28, NFR-000-17: la cabecera corrida dice cuándo se cierra la sesión."""
    pestana = abrir_pestana()
    _ir_a_inicio(pestana)
    assert CABECERA_SESION_FIJA not in texto_visible(pestana.pagina.content())
    _cargar_y_ver(pestana)

    expect(pestana.pagina.locator("#cabecera-corrida")).to_contain_text(CABECERA_SESION_FIJA)
    expect(pestana.pagina.get_by_role("button", name="Descartar el archivo")).to_be_visible()


# --- P-001-94: actividad y latido -------------------------------------------------------------


def _interactuar(pestana: Pestana, tipo: str) -> None:
    pagina = pestana.pagina
    if tipo == "puntero":
        pagina.mouse.move(200, 220)
        pagina.mouse.move(240, 260)
    elif tipo == "teclado":
        pagina.keyboard.press("Shift")
    elif tipo == "toque":
        pagina.dispatch_event("body", "touchstart")
    elif tipo == "foco":
        pagina.get_by_role("link", name="Cargar otro archivo").focus()
    elif tipo == "desplazamiento":
        pagina.evaluate("window.dispatchEvent(new Event('scroll'))")
    else:  # pragma: no cover - parámetros de la prueba
        raise AssertionError(tipo)


TIPOS_DE_ACTIVIDAD = ["puntero", "teclado", "toque", "foco", "desplazamiento"]


@pytest.mark.parametrize("tipo", TIPOS_DE_ACTIVIDAD)
def test_p_001_94_cada_tipo_de_actividad_cuenta_y_el_primero_tras_un_silencio_sale_de_inmediato(
    abrir_pestana: Callable[..., Pestana], tipo: str
) -> None:
    """P-001-94 · NFR-000-17, ADR-003 punto 5: puntero, teclado, toque, foco y desplazamiento."""
    pestana = abrir_pestana(simulado=True)
    _ir_a_inicio(pestana)
    _cargar_y_ver(pestana)
    _en_silencio(pestana)
    assert pestana.latidos() == 0

    _interactuar(pestana, tipo)

    assert _esperar(lambda: pestana.latidos() == 1), f"la actividad «{tipo}» no envió latido"
    _asentar()
    assert pestana.latidos() == 1


def test_p_001_94_como_maximo_un_latido_por_minuto_y_el_ultimo_se_envia_al_cumplirse_el_minuto(
    abrir_pestana: Callable[..., Pestana],
) -> None:
    """P-001-94 · NFR-000-17, ADR-003 punto 5: ráfagas de actividad, un latido por minuto."""
    pestana = abrir_pestana(simulado=True)
    _ir_a_inicio(pestana)
    _cargar_y_ver(pestana)
    _en_silencio(pestana)

    _interactuar(pestana, "puntero")
    assert _esperar(lambda: pestana.latidos() == 1)
    for segundo in (10, 20, 30, 40):
        _avanzar(pestana, 10 * 1000)
        for tipo in TIPOS_DE_ACTIVIDAD:
            _interactuar(pestana, tipo)
        _asentar(0.15)
        assert pestana.latidos() == 1, f"más de un latido antes del minuto (segundo {segundo})"

    # Al cumplirse el minuto sale un solo latido que recoge la actividad del intervalo.
    _avanzar(pestana, 20 * 1000 + 500)
    assert _esperar(lambda: pestana.latidos() == 2)
    _asentar()
    assert pestana.latidos() == 2
    # Sin más actividad no hay más latidos.
    _avanzar(pestana, 5 * MINUTO_MS)
    _asentar()
    assert pestana.latidos() == 2


def test_p_001_94_tras_un_silencio_de_mas_de_un_minuto_el_siguiente_latido_sale_de_inmediato(
    abrir_pestana: Callable[..., Pestana],
) -> None:
    """P-001-94 · ADR-003 punto 5: el primero tras un silencio no espera."""
    pestana = abrir_pestana(simulado=True)
    _ir_a_inicio(pestana)
    _cargar_y_ver(pestana)
    _en_silencio(pestana)

    _interactuar(pestana, "teclado")
    assert _esperar(lambda: pestana.latidos() == 1)
    _avanzar(pestana, 90 * 1000)
    _asentar()
    _interactuar(pestana, "teclado")
    assert _esperar(lambda: pestana.latidos() == 2)
    _asentar()
    assert pestana.latidos() == 2


def test_p_001_94_el_latido_reinicia_la_cuenta_del_servidor(
    abrir_pestana: Callable[..., Pestana], servidor: Servidor
) -> None:
    """P-001-94 · NFR-000-17: el latido llega al servidor, que mide desde él."""
    pestana = abrir_pestana(simulado=True)
    _ir_a_inicio(pestana)
    _cargar_y_ver(pestana)
    ficha = _ficha_de_la_pestana(pestana)
    assert ficha
    _en_silencio(pestana)

    servidor.reloj.avanzar(minutes=44)
    _interactuar(pestana, "teclado")
    assert _esperar(lambda: pestana.latidos() == 1)
    _esperar_actividad_en_el_servidor(servidor, ficha)
    servidor.reloj.avanzar(minutes=44)

    assert servidor.purgar() == 0
    assert servidor.almacen.obtener(ficha) is not None


# --- P-001-92: las cuatro formas de terminar, en el navegador ---------------------------------


def _terminar_descartando(pestana: Pestana, servidor: Servidor) -> None:
    pestana.pagina.get_by_role("button", name="Descartar el archivo").click()
    expect(pestana.pagina.get_by_text(E8_DESCARTE)).to_be_visible()


def _terminar_cerrando(pestana: Pestana, servidor: Servidor) -> None:
    _cerrar_la_pestana(pestana)
    assert _esperar_el_aviso_de_cierre(servidor) == 1


def _terminar_por_inactividad(pestana: Pestana, servidor: Servidor) -> None:
    _en_silencio(pestana)
    servidor.reloj.avanzar(minutes=45)
    _avanzar(pestana, 45 * MINUTO_MS)
    expect(pestana.pagina.get_by_text(E8_INACTIVIDAD)).to_be_visible()


def _terminar_por_error_de_contrato(pestana: Pestana, servidor: Servidor) -> None:
    pestana.pagina.get_by_role("link", name="Cargar otro archivo").click()
    _cargar(pestana, "cb14.xlsx", fixture("cb14_sin_nivel_de_evidencia.xlsx"))
    expect(
        pestana.pagina.get_by_role("alert").filter(
            has_text="No se pudo leer la matriz y la sesión terminó"
        )
    ).to_be_visible()


FORMAS_EN_NAVEGADOR: dict[str, Callable[[Pestana, Servidor], None]] = {
    "descarte": _terminar_descartando,
    "cierre_de_pestana": _terminar_cerrando,
    "inactividad": _terminar_por_inactividad,
    "error_de_contrato": _terminar_por_error_de_contrato,
}


@pytest.mark.parametrize("forma", list(FORMAS_EN_NAVEGADOR))
def test_p_001_92_tras_cada_forma_de_terminar_en_el_navegador_no_queda_ningun_marcador(
    abrir_pestana: Callable[..., Pestana],
    servidor: Servidor,
    caplog: pytest.LogCaptureFixture,
    forma: str,
) -> None:
    """P-001-92 · SC-000-17, NFR-000-17: sin marcadores en disco ni registros; la ficha no abre."""
    marcas = (*MARCADORES_CELDAS, NOMBRE_CON_MARCADOR)
    caplog.set_level(logging.DEBUG)
    rastros = RastrosEnDisco(marcas)
    pestana = abrir_pestana(simulado=(forma == "inactividad"))
    _ir_a_inicio(pestana)
    _cargar(pestana, NOMBRE_CON_MARCADOR, fixture("marcadores.xlsx"))
    _ver_cabecera(pestana, NOMBRE_CON_MARCADOR, 5)
    ficha = _ficha_de_la_pestana(pestana)
    assert ficha

    FORMAS_EN_NAVEGADOR[forma](pestana, servidor)

    # La sesión no se puede abrir con la ficha que tenía la pestaña.
    ya_no = _pedir(servidor.url, ficha, "/vista/resultado")
    assert not hay_resultados(texto_visible(ya_no))
    for marca in marcas:
        assert marca not in ya_no
    assert servidor.almacen.cantidad() == 0
    if forma != "cierre_de_pestana":
        assert _esperar(lambda: _ficha_de_la_pestana(pestana) is None)
        texto = texto_visible(pestana.pagina.content())
        assert not hay_resultados(texto)
        for marca in marcas:
            assert marca not in pestana.pagina.content()
    assert rastros.hallazgos() == []
    registros = texto_de_registros(caplog.records)
    for marca in (*marcas, ficha):
        assert marca not in registros


def test_p_001_92_una_interaccion_antes_de_los_45_minutos_mantiene_abierta_la_sesion(
    abrir_pestana: Callable[..., Pestana], servidor: Servidor
) -> None:
    """P-001-92 · NFR-000-17: la persona interactúa a los 44 min y la sesión sigue abierta."""
    pestana = abrir_pestana(simulado=True)
    _ir_a_inicio(pestana)
    _cargar_y_ver(pestana)
    ficha = _ficha_de_la_pestana(pestana)
    assert ficha
    _en_silencio(pestana)
    servidor.reloj.avanzar(minutes=44)
    _avanzar(pestana, 40 * MINUTO_MS)
    pestana.pagina.keyboard.press("Shift")
    assert _esperar(lambda: pestana.latidos() >= 1)
    _esperar_actividad_en_el_servidor(servidor, ficha)
    servidor.reloj.avanzar(minutes=44)
    _avanzar(pestana, MINUTO_MS)

    assert servidor.purgar() == 0
    _ver_cabecera(pestana, BASE, 5)
    assert servidor.almacen.cantidad() == 1
