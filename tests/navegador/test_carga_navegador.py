"""Fase 7 del plan 001, historia 4: cargar la matriz en un navegador real (T-001-61).

Pruebas P-001-85 y P-001-86, con la marca `navegador`. Corren aparte de las demás (plan 001, R-8):
necesitan Chromium (`python -m playwright install chromium`; la descarga la autoriza Jairo, R-7) y
la capa web completa (T-001-62 a T-001-70). Se escriben antes que ella y fallan mientras no exista.

Un servidor Uvicorn real, solo en `127.0.0.1`, sirve `app.servidor.crear_app` con el reloj
inyectado. Los archivos se entregan al navegador desde la memoria (nada se escribe en disco).
axe-core viene dentro de `axe-playwright-python`: la revisión de accesibilidad no usa la red.

Supuestos de interfaz que flujos.md y el boceto `carga.html` fijan y que estas pruebas usan:
control de archivo con la etiqueta «Archivo de la matriz (Excel .xlsx, hasta 15 MB)», botón
«Cargar la matriz», vínculo o botón «Cargar otro archivo» en la cabecera corrida, estado E1 con
`role="status"` y el texto «Leyendo la matriz. Esto puede tardar unos segundos.», mensajes de
rechazo con `role="alert"` y su título como encabezado que recibe el foco.
`[NEEDS CLARIFICATION: si elegir el archivo envía solo o hace falta pulsar «Cargar la matriz»;
flujos.md §3 dice que se pulsa el botón.]`
"""

import re
from collections.abc import Callable, Iterator
from dataclasses import dataclass, field
from typing import Any

import pytest
from playwright.sync_api import Page, expect

from tests.ayudas_web import (
    CUERPO_E2,
    CUERPO_E3,
    CUERPO_E10,
    ETIQUETA_ARCHIVO,
    LIMITE_BYTES,
    LIMITE_DESCOMPRIMIDO,
    MIME_XLSX,
    TITULO_RECHAZO,
    Reloj,
    cabecera_esperada,
    crear_app,
    descomprimido_declarado,
    exacto_en_bytes,
    fixture,
    servidor_real,
)

pytestmark = pytest.mark.navegador

BASE = "base_valida.xlsx"
TEXTO_E1 = "Leyendo la matriz. Esto puede tardar unos segundos."
ETIQUETAS_WCAG = ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"]
ANCHO_DE_ESCRITORIO = 1280
ANCHO_MINIMO = 360


# --- Servidor y páginas -----------------------------------------------------------------------


@pytest.fixture(scope="module")
def url_del_servidor() -> Iterator[str]:
    """Un servidor Uvicorn real en `127.0.0.1` y en un puerto libre, sin registro de accesos."""
    with servidor_real(crear_app(reloj=Reloj())) as url:
        yield url


@dataclass
class Pestana:
    """Una pestaña con lo que el navegador hizo mientras estuvo abierta."""

    pagina: Page
    url: str
    peticiones: list[str] = field(default_factory=list)
    consola: list[tuple[str, str]] = field(default_factory=list)


@pytest.fixture
def abrir_pestana(browser: Any, url_del_servidor: str) -> Iterator[Callable[..., Pestana]]:
    """Fábrica de pestañas, cada una en su propio contexto (sin almacenamiento compartido)."""
    contextos: list[Any] = []

    def abrir(ancho: int = ANCHO_DE_ESCRITORIO, esquema: str = "light") -> Pestana:
        contexto = browser.new_context(
            viewport={"width": ancho, "height": 900}, color_scheme=esquema, locale="es-CO"
        )
        contextos.append(contexto)
        pagina = contexto.new_page()
        pestana = Pestana(pagina, url_del_servidor)
        pagina.on("request", lambda peticion: pestana.peticiones.append(peticion.url))
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


def _elegir_y_cargar(pestana: Pestana, nombre: str, contenido: bytes) -> None:
    pagina = pestana.pagina
    pagina.get_by_label(ETIQUETA_ARCHIVO).set_input_files(
        files=[{"name": nombre, "mimeType": MIME_XLSX, "buffer": contenido}]
    )
    pagina.get_by_role("button", name="Cargar la matriz").click()


def _ver_cabecera(pestana: Pestana, nombre: str, n_documentos: int) -> None:
    # La cabecera corrida es el único sitio que se comprueba: el colofón y el anuncio
    # accesible repiten el mismo texto y harían ambigua una búsqueda en toda la página.
    corte = pestana.pagina.locator("#cabecera-corrida .corte")
    expect(corte).to_have_text(cabecera_esperada(nombre, n_documentos))


# --- P-001-85 ---------------------------------------------------------------------------------


def test_p_001_85_cargar_en_chromium_muestra_e1_y_luego_la_cabecera_con_todo_en_local(
    abrir_pestana: Callable[..., Pestana],
) -> None:
    """P-001-85 · SC-000-15, NFR-000-15, US-001-4.1: elegir, ver E1 y luego la cabecera."""
    pestana = abrir_pestana()
    pagina = pestana.pagina
    retenidas: list[Any] = []
    pagina.route("**/carga", lambda ruta: retenidas.append(ruta))
    assert pestana.url.startswith("http://127.0.0.1:")
    _ir_a_inicio(pestana)

    _elegir_y_cargar(pestana, BASE, fixture(BASE))

    # E1: mientras la respuesta no llega, el aviso se anuncia y el botón queda inactivo.
    estado = pagina.get_by_role("status").filter(has_text=TEXTO_E1)
    expect(estado).to_be_visible()
    expect(pagina.get_by_role("button", name="Cargar la matriz")).to_be_disabled()
    assert len(retenidas) == 1
    retenidas[0].continue_()

    _ver_cabecera(pestana, BASE, 5)
    expect(estado).to_have_count(0)
    # Todas las peticiones fueron a 127.0.0.1 (ningún recurso ni servicio externo).
    assert pestana.peticiones
    for peticion in pestana.peticiones:
        assert peticion.startswith(("http://127.0.0.1:", "data:")), peticion


# --- P-001-86 ---------------------------------------------------------------------------------


def _estado_v0(pestana: Pestana) -> None:
    _ir_a_inicio(pestana)


def _rechazo(nombre: str, contenido: Callable[[], bytes], titulo: str) -> Callable[[Pestana], None]:
    def llevar(pestana: Pestana) -> None:
        _ir_a_inicio(pestana)
        _elegir_y_cargar(pestana, nombre, contenido())
        expect(pestana.pagina.get_by_role("alert").filter(has_text=titulo)).to_be_visible()

    return llevar


def _estado_v2(nombre: str) -> Callable[[Pestana], None]:
    def llevar(pestana: Pestana) -> None:
        _ir_a_inicio(pestana)
        _elegir_y_cargar(pestana, nombre, fixture(nombre))
        _ver_cabecera(pestana, nombre, 5)
        expect(pestana.pagina.get_by_text("Antes de leer los resultados")).to_be_visible()

    return llevar


def _bytes_e3() -> bytes:
    return exacto_en_bytes(LIMITE_BYTES + 1)


def _bytes_e10() -> bytes:
    return descomprimido_declarado(LIMITE_DESCOMPRIMIDO + 1)


E2 = _rechazo("cb16_otro_tipo.txt", lambda: fixture("cb16_otro_tipo.txt"), TITULO_RECHAZO)
E3 = _rechazo("mas_uno.xlsx", _bytes_e3, TITULO_RECHAZO)
E10 = _rechazo("contenido_grande.xlsx", _bytes_e10, TITULO_RECHAZO)
E4 = _rechazo(
    "cb14.xlsx", lambda: fixture("cb14_sin_nivel_de_evidencia.xlsx"), "No se pudo leer la matriz"
)

TITULO_E4_PREVIA_RE = r"No se pudo leer la matriz y la sesión terminó"


def _con_previa(
    nombre: str, contenido: Callable[[], bytes], titulo: str
) -> Callable[[Pestana], None]:
    def llevar(pestana: Pestana) -> None:
        _ir_a_inicio(pestana)
        _elegir_y_cargar(pestana, BASE, fixture(BASE))
        _ver_cabecera(pestana, BASE, 5)
        pestana.pagina.get_by_text("Cargar otro archivo").click()
        expect(pestana.pagina.get_by_label(ETIQUETA_ARCHIVO)).to_be_visible()
        _elegir_y_cargar(pestana, nombre, contenido())
        expect(pestana.pagina.get_by_role("alert").filter(has_text=titulo)).to_be_visible()

    return llevar


# Estados de la historia 4 (id → cómo llegar a él). Los de matriz previa siguen a «E2 / E3 / E10 con
# matriz previa» y «E4 con matriz previa» de flujos.md §2.
ESTADOS: dict[str, Callable[[Pestana], None]] = {
    "V0": _estado_v0,
    "E2": E2,
    "E3": E3,
    "E10": E10,
    "E4": E4,
    "E3_con_matriz_previa": _con_previa("mas_uno.xlsx", _bytes_e3, TITULO_RECHAZO),
    "E10_con_matriz_previa": _con_previa("contenido_grande.xlsx", _bytes_e10, TITULO_RECHAZO),
    "E4_con_matriz_previa": _con_previa(
        "cb14.xlsx",
        lambda: fixture("cb14_sin_nivel_de_evidencia.xlsx"),
        TITULO_E4_PREVIA_RE,
    ),
    "V2_cabecera_y_colofon": _estado_v2(BASE),
    "V2_con_advertencias": _estado_v2("esc_2_1_fuera_de_lista_n3.xlsx"),
}

# Estados con mensaje (role="alert"): el texto del título que recibe el foco.
TITULOS_CON_FOCO = {
    "E2": r"^No se pudo cargar el archivo$",
    "E3": r"^No se pudo cargar el archivo$",
    "E10": r"^No se pudo cargar el archivo$",
    "E4": r"^No se pudo leer la matriz$",
    "E3_con_matriz_previa": r"^No se pudo cargar el archivo$",
    "E10_con_matriz_previa": r"^No se pudo cargar el archivo$",
    "E4_con_matriz_previa": r"^No se pudo leer la matriz y la sesión terminó$",
}


@pytest.mark.parametrize("esquema", ["light", "dark"])
@pytest.mark.parametrize("estado", list(ESTADOS))
def test_p_001_86_axe_no_halla_problemas_de_nivel_a_ni_aa(
    abrir_pestana: Callable[..., Pestana], estado: str, esquema: str
) -> None:
    """P-001-86 · SC-000-04, NFR-000-04: axe-core sin hallazgos A o AA en V0, E2 a E10 y V2."""
    from axe_playwright_python.sync_playwright import Axe

    pestana = abrir_pestana(esquema=esquema)
    ESTADOS[estado](pestana)

    resultados = Axe().run(
        pestana.pagina,
        options={
            "runOnly": {"type": "tag", "values": ETIQUETAS_WCAG},
            "resultTypes": ["violations"],
        },
    )

    hallazgos = [
        f"{v['id']} ({v['impact']}): {len(v['nodes'])} elementos"
        for v in resultados.response["violations"]
    ]
    assert hallazgos == []


@pytest.mark.parametrize("estado", list(ESTADOS))
def test_p_001_86_a_360_px_no_hay_desplazamiento_horizontal(
    abrir_pestana: Callable[..., Pestana], estado: str
) -> None:
    """P-001-86 · SC-000-05 (base), NFR-000-05: a 360 px la página no se desplaza en horizontal."""
    pestana = abrir_pestana(ancho=ANCHO_MINIMO)
    ESTADOS[estado](pestana)

    ancho_del_contenido, ancho_visible = pestana.pagina.evaluate(
        "[document.documentElement.scrollWidth, document.documentElement.clientWidth]"
    )

    assert ancho_visible <= ANCHO_MINIMO
    assert ancho_del_contenido <= ancho_visible


@pytest.mark.parametrize("estado", list(TITULOS_CON_FOCO))
def test_p_001_86_el_mensaje_se_anuncia_y_el_foco_pasa_a_su_titulo(
    abrir_pestana: Callable[..., Pestana], estado: str
) -> None:
    """P-001-86 · NFR-000-04, flujos.md §2: `role="alert"` y foco en el título del mensaje."""
    pestana = abrir_pestana()
    ESTADOS[estado](pestana)
    pagina = pestana.pagina

    titulo = re.compile(TITULOS_CON_FOCO[estado])
    expect(pagina.locator(":focus")).to_have_text(titulo)
    enfocado = pagina.evaluate("document.activeElement.tagName.toLowerCase()")
    assert enfocado in {"h1", "h2", "h3"}
    mensaje = pagina.get_by_role("alert").filter(has=pagina.locator(":focus"))
    expect(mensaje).to_have_count(1)
    # El texto del rechazo, tal como lo fija flujos.md §2.
    cuerpo = {"E2": CUERPO_E2, "E3": CUERPO_E3, "E10": CUERPO_E10}.get(estado.split("_")[0])
    if cuerpo is not None:
        expect(mensaje).to_contain_text(cuerpo)


@pytest.mark.parametrize("estado", ["V0", "V2_cabecera_y_colofon"])
def test_p_001_86_la_consola_no_muestra_errores_de_la_politica_de_contenido(
    abrir_pestana: Callable[..., Pestana], estado: str
) -> None:
    """P-001-86 · NFR-000-04, ADR-003 punto 6, R-6: sin errores de política de contenido."""
    pestana = abrir_pestana()
    ESTADOS[estado](pestana)

    errores = [
        (tipo, texto)
        for tipo, texto in pestana.consola
        if tipo in {"error", "pageerror"} or "Content Security Policy" in texto
    ]
    assert errores == []
