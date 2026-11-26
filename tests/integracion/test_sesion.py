"""Fase 8 del plan 001, historia 5: terminar la sesión desde la capa web (T-001-80).

Pruebas P-001-89, P-001-91 y P-001-95, la parte de cliente de pruebas de P-001-92 y la parte del
servidor de P-001-90 (el período de gracia de 10 s tras el aviso de cierre; la parte del navegador
está en `tests/navegador/test_sesion_navegador.py`). Se escribieron antes que la implementación de
M15 (T-001-82) y de las rutas de M14 (T-001-83) y fallaron mientras no existieron.

Cliente de pruebas de Starlette sobre `app.servidor.crear_app` con el reloj inyectado
(`tests.ayudas_web.Reloj`): el tiempo avanza solo cuando la prueba lo avanza. Rutas de la tabla
«Rutas de la capa web» del plan 001: `POST /sesion/descartar`, `POST /sesion/latido` y
`POST /sesion/cierre`, con la ficha en `X-EGM-Sesion`.

Esperados escritos a mano a partir de `docs/interfaz/flujos.md` §2 (E7, E8, E9) y §3 (F-001-5), de
ADR-003 (puntos 5 y 9), de NFR-000-17 y de los docstrings del constructor de fixtures (5 documentos
en `base_valida`, `marcadores` y `sesion_a`; 8 en `sesion_b`). Ningún dato viene de la lámina 7.

`[NEEDS CLARIFICATION: los documentos no fijan los códigos de respuesta de las rutas de sesión ni
cómo se muestra E8 de inactividad; se supone: latido y cierre responden 204; el latido de una ficha
que ya no abre nada responde 410; la ficha de una sesión terminada por inactividad recibe E8 una
sola vez en la siguiente petición de `GET /vista/inicio` o `GET /vista/resultado`.]`
"""

import logging
import re
import time
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import timedelta
from typing import Any

import pytest

from tests.ayudas_web import (
    E8_DESCARTE,
    E8_INACTIVIDAD,
    GRACIA_CIERRE,
    INACTIVIDAD,
    RUTA_CIERRE,
    RUTA_DESCARTAR,
    RUTA_LATIDO,
    RastrosEnDisco,
    Reloj,
    cabecera_esperada,
    cargar,
    cliente_de,
    crear_app,
    enviar_a_sesion,
    ficha_de,
    fixture,
    hay_resultados,
    resultado,
    texto_de_registros,
    texto_visible,
)
from tests.constructor import MARCADORES_CELDAS, NOMBRE_CON_MARCADOR

BASE = "base_valida.xlsx"


@contextmanager
def _servicio(reloj: Reloj | None = None) -> Iterator[tuple[Any, Reloj, Any]]:
    """La aplicación en marcha (con su ciclo de vida): cliente, reloj y almacén de sesiones."""
    reloj = reloj if reloj is not None else Reloj()
    app = crear_app(reloj=reloj)
    with cliente_de(app) as cliente:
        yield cliente, reloj, app.state.servicios.almacen


def _texto(respuesta: Any) -> str:
    return texto_visible(respuesta.text)


def _ficha(cliente: Any, nombre: str = BASE) -> str:
    """Carga un fixture y devuelve la ficha de su sesión."""
    return ficha_de(cargar(cliente, fixture(nombre), nombre))


def _abre(cliente: Any, ficha: str) -> bool:
    """Si la ficha todavía abre los resultados de su matriz (sin que la consulta cambie nada)."""
    return hay_resultados(_texto(resultado(cliente, ficha)))


def _purgar(almacen: Any, reloj: Reloj) -> int:
    return almacen.purgar_vencidas(reloj())


def _espiar_terminar(monkeypatch: pytest.MonkeyPatch) -> list[tuple[str, str]]:
    """Registra (ficha, causa) de cada `terminar` de `AlmacenSesiones` (M15)."""
    from app import sesiones

    llamadas: list[tuple[str, str]] = []
    original = sesiones.AlmacenSesiones.terminar

    def envoltura(self: Any, ficha: str, causa: Any) -> Any:
        llamadas.append((ficha, str(causa)))
        return original(self, ficha, causa)

    monkeypatch.setattr(sesiones.AlmacenSesiones, "terminar", envoltura)
    return llamadas


# --- Valores fijos de M15 ---------------------------------------------------------------------


def test_p_001_91_la_inactividad_es_de_45_minutos_y_la_gracia_de_10_segundos_y_son_fijas() -> None:
    """P-001-91 · NFR-000-17, ADR-003 punto 9: valores fijos, no configurables."""
    from app import sesiones
    from app.configuracion import Configuracion

    assert sesiones.INACTIVIDAD == INACTIVIDAD == timedelta(minutes=45)
    assert sesiones.GRACIA_CIERRE == GRACIA_CIERRE == timedelta(seconds=10)
    campos = set(Configuracion.__dataclass_fields__)
    assert not {c for c in campos if "inactiv" in c.lower() or "gracia" in c.lower()}


# --- P-001-89 ---------------------------------------------------------------------------------


def test_p_001_89_descartar_termina_la_sesion_con_e8_y_sin_cifras(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """P-001-89 · US-001-5.1, FR-001-28: E8 «Descartó el archivo…», sin cifras; la ficha no abre."""
    with _servicio() as (cliente, _reloj, almacen):
        ficha = _ficha(cliente)
        assert _abre(cliente, ficha)
        terminadas = _espiar_terminar(monkeypatch)
        respuesta = enviar_a_sesion(cliente, RUTA_DESCARTAR, ficha)
        despues = resultado(cliente, ficha)
        latido = enviar_a_sesion(cliente, RUTA_LATIDO, ficha)

        assert almacen.cantidad() == 0

    assert respuesta.status_code == 200
    assert respuesta.headers["X-EGM-Destino"] == "contenido"
    texto = _texto(respuesta)
    assert E8_DESCARTE in texto
    assert "Cargue la matriz bibliográfica" in texto  # la vista de carga
    assert not hay_resultados(texto)
    assert BASE not in texto
    assert "5 documentos" not in texto
    assert [causa for _, causa in terminadas] == ["descarte"]
    assert terminadas[0][0] == ficha
    # La ficha ya no abre nada, y no vuelve a mostrar ningún mensaje de sesión terminada.
    assert despues.status_code == 200
    assert not hay_resultados(_texto(despues))
    assert E8_DESCARTE not in _texto(despues)
    assert latido.status_code == 410


def test_p_001_89_el_texto_de_e8_se_anuncia_como_estado_y_recibe_el_foco() -> None:
    """P-001-89 · US-001-5.1, NFR-000-04: E8 con `role="status"` y su primer párrafo con el foco."""
    with _servicio() as (cliente, _reloj, _almacen):
        ficha = _ficha(cliente)
        respuesta = enviar_a_sesion(cliente, RUTA_DESCARTAR, ficha)

    html = respuesta.text
    assert re.search(r'<div class="mensaje" role="status">', html)
    assert "data-egm-foco" in html
    # La cabecera corrida se vacía: sin la línea de la matriz ni los botones de la sesión.
    assert "Matriz:" not in html
    assert "data-egm-descartar" not in html


def test_p_001_89_descartar_sin_sesion_no_inventa_un_mensaje() -> None:
    """P-001-89 · FR-001-28: sin sesión que descartar, la vista de carga queda sin mensaje."""
    with _servicio() as (cliente, _reloj, _almacen):
        sin_ficha = enviar_a_sesion(cliente, RUTA_DESCARTAR, None)
        inventada = enviar_a_sesion(cliente, RUTA_DESCARTAR, "x" * 43)

    for respuesta in (sin_ficha, inventada):
        assert respuesta.status_code == 200
        assert E8_DESCARTE not in _texto(respuesta)
        assert "Cargue la matriz bibliográfica" in _texto(respuesta)
        assert not hay_resultados(_texto(respuesta))


def test_p_001_89_las_rutas_de_sesion_solo_admiten_post() -> None:
    """P-001-89 · NFR-000-17: descartar, latido y cierre no se pueden pedir con GET."""
    with _servicio() as (cliente, _reloj, _almacen):
        ficha = _ficha(cliente)
        estados = [
            cliente.get(ruta, headers={"X-EGM-Sesion": ficha}).status_code
            for ruta in (RUTA_DESCARTAR, RUTA_LATIDO, RUTA_CIERRE)
        ]
        sigue = _abre(cliente, ficha)

    assert estados == [405, 405, 405]
    assert sigue


# --- P-001-91: inactividad --------------------------------------------------------------------


def test_p_001_91_a_44_min_59_s_la_sesion_sigue_y_a_45_min_se_purga() -> None:
    """P-001-91 · US-001-5.3, NFR-000-17: el límite es de 45 minutos, no antes."""
    with _servicio() as (cliente, reloj, almacen):
        ficha = _ficha(cliente)
        reloj.avanzar(minutes=44, seconds=59)
        antes = _purgar(almacen, reloj)
        sigue = almacen.obtener(ficha) is not None
        reloj.avanzar(seconds=1)
        purgadas = _purgar(almacen, reloj)
        despues = almacen.obtener(ficha)

    assert antes == 0
    assert sigue
    assert purgadas == 1
    assert despues is None


def test_p_001_91_pasados_45_minutos_la_ficha_ya_no_abre_y_se_muestra_e8_de_inactividad() -> None:
    """P-001-91 · US-001-5.3: mensaje E8 de inactividad, sin cifras, una sola vez."""
    with _servicio() as (cliente, reloj, almacen):
        ficha = _ficha(cliente)
        reloj.avanzar(minutes=45)
        _purgar(almacen, reloj)
        primera = resultado(cliente, ficha)
        segunda = resultado(cliente, ficha)

    texto = _texto(primera)
    assert E8_INACTIVIDAD in texto
    assert "Cargue la matriz bibliográfica" in texto
    assert not hay_resultados(texto)
    assert BASE not in texto
    # El aviso se da una vez: la segunda consulta ve la vista de carga sin mensaje (E9).
    assert E8_INACTIVIDAD not in _texto(segunda)
    assert not hay_resultados(_texto(segunda))


def test_p_001_91_sin_esperar_a_la_purga_una_sesion_vencida_no_se_abre() -> None:
    """P-001-91 · NFR-000-17: una sesión vencida no se sirve aunque la purga no haya corrido."""
    with _servicio() as (cliente, reloj, _almacen):
        ficha = _ficha(cliente)
        reloj.avanzar(minutes=44, seconds=59)
        sigue = _abre(cliente, ficha)  # esta petición cuenta como actividad (ADR-003, punto 5)
        reloj.avanzar(minutes=44, seconds=59)
        sigue_otra_vez = _abre(cliente, ficha)
        reloj.avanzar(minutes=45)
        respuesta = resultado(cliente, ficha)

    assert sigue
    assert sigue_otra_vez
    assert E8_INACTIVIDAD in _texto(respuesta)
    assert not hay_resultados(_texto(respuesta))


def test_p_001_91_el_latido_reinicia_la_cuenta_y_nada_mas_que_el_latido() -> None:
    """P-001-91 · NFR-000-17, ADR-003 punto 5: se mide desde el último latido o petición."""
    with _servicio() as (cliente, reloj, almacen):
        ficha = _ficha(cliente)
        reloj.avanzar(minutes=44)
        latido = enviar_a_sesion(cliente, RUTA_LATIDO, ficha)
        reloj.avanzar(minutes=44)
        _purgar(almacen, reloj)
        sigue = almacen.obtener(ficha) is not None
        reloj.avanzar(minutes=1)
        purgadas = _purgar(almacen, reloj)

    assert latido.status_code == 204
    assert latido.content == b""
    assert sigue
    assert purgadas == 1


def test_p_001_91_un_latido_de_una_sesion_vencida_no_la_revive_y_pide_volver_a_cargar() -> None:
    """P-001-91 · NFR-000-17: el latido tardío no abre nada; la vista de carga trae E8."""
    with _servicio() as (cliente, reloj, almacen):
        ficha = _ficha(cliente)
        reloj.avanzar(minutes=45)
        latido = enviar_a_sesion(cliente, RUTA_LATIDO, ficha)
        inicio = cliente.get("/vista/inicio", headers={"X-EGM-Sesion": ficha})
        cantidad = almacen.cantidad()

    assert latido.status_code == 410
    assert cantidad == 0
    assert E8_INACTIVIDAD in _texto(inicio)
    assert not hay_resultados(_texto(inicio))


def test_p_001_91_el_latido_sin_ficha_o_con_ficha_inventada_no_abre_nada() -> None:
    """P-001-91 · NFR-000-17, NFR-000-18: un latido sin sesión responde 410 y no crea nada."""
    with _servicio() as (cliente, _reloj, almacen):
        sin_ficha = enviar_a_sesion(cliente, RUTA_LATIDO, None)
        inventada = enviar_a_sesion(cliente, RUTA_LATIDO, "x" * 43)
        cantidad = almacen.cantidad()

    assert sin_ficha.status_code == 410
    assert inventada.status_code == 410
    assert cantidad == 0


def test_p_001_91_una_carga_nueva_cuenta_como_actividad() -> None:
    """P-001-91 · NFR-000-17, ADR-003 punto 5: cargar otro archivo reinicia los 45 minutos."""
    with _servicio() as (cliente, reloj, almacen):
        ficha = _ficha(cliente)
        reloj.avanzar(minutes=44)
        cargar(cliente, fixture("sesion_b.xlsx"), "sesion_b.xlsx", ficha)
        reloj.avanzar(minutes=44)
        purgadas = _purgar(almacen, reloj)
        sigue = almacen.obtener(ficha) is not None

    assert purgadas == 0
    assert sigue


def test_p_001_91_una_carga_con_una_ficha_vencida_crea_una_sesion_nueva() -> None:
    """P-001-91 · FR-001-20, NFR-000-17: la ficha vencida no sirve para reemplazar nada."""
    with _servicio() as (cliente, reloj, _almacen):
        ficha = _ficha(cliente)
        reloj.avanzar(minutes=45)
        respuesta = cargar(cliente, fixture("sesion_b.xlsx"), "sesion_b.xlsx", ficha)
        nueva = ficha_de(respuesta)

    assert respuesta.status_code == 200
    assert nueva
    assert nueva != ficha
    assert cabecera_esperada("sesion_b.xlsx", 8) in _texto(respuesta)


# --- Cierre de pestaña (ADR-003, punto 9): parte del servidor de P-001-90 y de P-001-92 -------


def test_p_001_90_pasados_10_segundos_del_aviso_de_cierre_el_servidor_borra_la_sesion() -> None:
    """P-001-90 · US-001-5.2, ADR-003 punto 9: a 9 s 999 sigue, a 10 s se borra."""
    with _servicio() as (cliente, reloj, almacen):
        ficha = _ficha(cliente)
        aviso = enviar_a_sesion(cliente, RUTA_CIERRE, ficha)
        reloj.avanzar(seconds=9, milliseconds=999)
        antes = _purgar(almacen, reloj)
        sigue = almacen.obtener(ficha) is not None
        reloj.avanzar(milliseconds=1)
        purgadas = _purgar(almacen, reloj)
        despues = resultado(cliente, ficha)

    assert aviso.status_code == 204
    assert antes == 0
    assert sigue
    assert purgadas == 1
    # Cerrar la pestaña no es inactividad: ninguna cifra y ningún mensaje al volver a abrir.
    assert not hay_resultados(_texto(despues))
    assert E8_INACTIVIDAD not in _texto(despues)
    assert E8_DESCARTE not in _texto(despues)


def test_p_001_90_recargar_antes_de_10_segundos_conserva_la_sesion() -> None:
    """P-001-90 · US-001-5.2, ADR-003 punto 9: la ficha vuelve con la recarga y la sesión sigue."""
    with _servicio() as (cliente, reloj, almacen):
        ficha = _ficha(cliente)
        enviar_a_sesion(cliente, RUTA_CIERRE, ficha)
        reloj.avanzar(seconds=5)
        recarga = resultado(cliente, ficha)
        reloj.avanzar(seconds=30)
        purgadas = _purgar(almacen, reloj)
        sigue = almacen.obtener(ficha) is not None

    assert hay_resultados(_texto(recarga))
    assert purgadas == 0
    assert sigue


def test_p_001_90_un_latido_antes_de_los_10_segundos_tambien_cancela_el_borrado() -> None:
    """P-001-90 · ADR-003 punto 9: la misma ficha que vuelve, por cualquier petición, cancela."""
    with _servicio() as (cliente, reloj, almacen):
        ficha = _ficha(cliente)
        enviar_a_sesion(cliente, RUTA_CIERRE, ficha)
        reloj.avanzar(seconds=5)
        latido = enviar_a_sesion(cliente, RUTA_LATIDO, ficha)
        reloj.avanzar(seconds=30)
        purgadas = _purgar(almacen, reloj)

    assert latido.status_code == 204
    assert purgadas == 0
    assert almacen.cantidad() == 1


def test_p_001_90_un_segundo_aviso_despues_de_la_recarga_vuelve_a_dar_10_segundos() -> None:
    """P-001-90 · ADR-003 punto 9: el plazo se cuenta desde el último aviso."""
    with _servicio() as (cliente, reloj, almacen):
        ficha = _ficha(cliente)
        enviar_a_sesion(cliente, RUTA_CIERRE, ficha)
        reloj.avanzar(seconds=5)
        resultado(cliente, ficha)
        reloj.avanzar(seconds=20)
        enviar_a_sesion(cliente, RUTA_CIERRE, ficha)
        reloj.avanzar(seconds=9)
        antes = _purgar(almacen, reloj)
        reloj.avanzar(seconds=1)
        despues = _purgar(almacen, reloj)

    assert antes == 0
    assert despues == 1


def test_p_001_90_el_aviso_de_cierre_no_revela_si_la_ficha_existe_ni_crea_nada() -> None:
    """P-001-90 · NFR-000-17, NFR-000-18: la misma respuesta con ficha, sin ella o inventada."""
    with _servicio() as (cliente, _reloj, almacen):
        ficha = _ficha(cliente)
        respuestas = [
            enviar_a_sesion(cliente, RUTA_CIERRE, ficha),
            enviar_a_sesion(cliente, RUTA_CIERRE, None),
            enviar_a_sesion(cliente, RUTA_CIERRE, "x" * 43),
        ]
        cantidad = almacen.cantidad()

    assert [r.status_code for r in respuestas] == [204, 204, 204]
    assert [r.content for r in respuestas] == [b"", b"", b""]
    assert cantidad == 1


def test_p_001_90_el_aviso_de_cierre_no_cuenta_como_actividad() -> None:
    """P-001-90 · NFR-000-17: avisar el cierre no extiende los 45 minutos."""
    with _servicio() as (cliente, reloj, almacen):
        ficha = _ficha(cliente)
        reloj.avanzar(minutes=44, seconds=55)
        enviar_a_sesion(cliente, RUTA_CIERRE, ficha)
        reloj.avanzar(seconds=5)
        purgadas = _purgar(almacen, reloj)
        despues = resultado(cliente, ficha)

    # A los 45 minutos de la última actividad termina por inactividad, aunque la gracia siga.
    assert purgadas == 1
    assert E8_INACTIVIDAD in _texto(despues)


# --- Tarea periódica de purga (T-001-82) ------------------------------------------------------


def _esperar(condicion: Any, segundos: float = 5.0) -> bool:
    plazo = time.monotonic() + segundos
    while time.monotonic() < plazo:
        if condicion():
            return True
        time.sleep(0.01)
    return bool(condicion())


def test_t_001_82_la_tarea_periodica_purga_sola_y_se_detiene_con_la_aplicacion(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """P-001-91, P-001-90 · NFR-000-17: la purga corre atada al ciclo de vida de la aplicación."""
    from app import servidor

    monkeypatch.setattr(servidor, "INTERVALO_DE_PURGA", timedelta(milliseconds=20))
    reloj = Reloj()
    app = crear_app(reloj=reloj)
    with cliente_de(app) as cliente:
        almacen = app.state.servicios.almacen
        ficha_inactiva = _ficha(cliente)
        ficha_cerrada = _ficha(cliente, "sesion_b.xlsx")
        ficha_viva = _ficha(cliente, "sesion_a.xlsx")
        enviar_a_sesion(cliente, RUTA_CIERRE, ficha_cerrada)
        assert almacen.cantidad() == 3
        tarea = app.state.purga
        assert not tarea.done()

        reloj.avanzar(seconds=10)
        assert _esperar(lambda: almacen.cantidad() == 2), "la purga no borró la del cierre"
        enviar_a_sesion(cliente, RUTA_LATIDO, ficha_viva)
        reloj.avanzar(minutes=44, seconds=59)
        enviar_a_sesion(cliente, RUTA_LATIDO, ficha_viva)
        reloj.avanzar(minutes=1)
        assert _esperar(lambda: almacen.cantidad() == 1), "la purga no borró la inactiva"
        assert almacen.obtener(ficha_viva) is not None
        assert almacen.obtener(ficha_inactiva) is None

    assert tarea.done()


def test_t_001_82_un_fallo_de_la_purga_no_la_detiene_y_se_registra_solo_por_tipo(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    """NFR-000-17, M14: la tarea sigue tras un error y el registro no trae su mensaje."""
    from app import servidor, sesiones

    secreto = "MARCA-FALLO-DE-PURGA-77C1"
    llamadas: list[int] = []
    original = sesiones.AlmacenSesiones.purgar_vencidas

    def falla_una_vez(self: Any, ahora: Any) -> int:
        llamadas.append(1)
        if len(llamadas) == 1:
            raise RuntimeError(secreto)
        return int(original(self, ahora))

    monkeypatch.setattr(servidor, "INTERVALO_DE_PURGA", timedelta(milliseconds=10))
    monkeypatch.setattr(sesiones.AlmacenSesiones, "purgar_vencidas", falla_una_vez)
    caplog.set_level(logging.DEBUG)
    app = crear_app()
    with cliente_de(app):
        assert _esperar(lambda: len(llamadas) >= 3), "la tarea se detuvo tras el fallo"

    registros = texto_de_registros(caplog.records)
    assert secreto not in registros
    assert "RuntimeError" in registros


# --- P-001-92: ningún rastro tras terminar la sesión -----------------------------------------


def _terminar_por_descarte(cliente: Any, reloj: Reloj, almacen: Any, ficha: str) -> None:
    assert enviar_a_sesion(cliente, RUTA_DESCARTAR, ficha).status_code == 200


def _terminar_por_cierre(cliente: Any, reloj: Reloj, almacen: Any, ficha: str) -> None:
    enviar_a_sesion(cliente, RUTA_CIERRE, ficha)
    reloj.avanzar(seconds=10)
    assert _purgar(almacen, reloj) == 1


def _terminar_por_inactividad(cliente: Any, reloj: Reloj, almacen: Any, ficha: str) -> None:
    reloj.avanzar(minutes=45)
    assert _purgar(almacen, reloj) == 1


def _terminar_por_error_de_contrato(cliente: Any, reloj: Reloj, almacen: Any, ficha: str) -> None:
    respuesta = cargar(cliente, fixture("cb14_sin_nivel_de_evidencia.xlsx"), "cb14.xlsx", ficha)
    assert respuesta.status_code == 422


FORMAS = {
    "descarte": _terminar_por_descarte,
    "cierre_de_pestana": _terminar_por_cierre,
    "inactividad": _terminar_por_inactividad,
    "error_de_contrato": _terminar_por_error_de_contrato,
}


@pytest.mark.parametrize("forma", list(FORMAS))
def test_p_001_92_tras_cada_forma_de_terminar_no_queda_ningun_marcador_y_la_sesion_no_abre(
    forma: str, caplog: pytest.LogCaptureFixture
) -> None:
    """P-001-92 · SC-000-17, NFR-000-17: sin marcadores en disco ni registros; la ficha no abre."""
    marcas = (*MARCADORES_CELDAS, NOMBRE_CON_MARCADOR)
    caplog.set_level(logging.DEBUG)
    rastros = RastrosEnDisco(marcas)
    with _servicio() as (cliente, reloj, almacen):
        ficha = ficha_de(cargar(cliente, fixture("marcadores.xlsx"), NOMBRE_CON_MARCADOR))
        assert _abre(cliente, ficha)

        FORMAS[forma](cliente, reloj, almacen, ficha)
        despues = resultado(cliente, ficha)
        latido = enviar_a_sesion(cliente, RUTA_LATIDO, ficha)
        cantidad = almacen.cantidad()

    assert cantidad == 0
    assert latido.status_code == 410
    assert not hay_resultados(_texto(despues))
    for marca in marcas:
        assert marca not in despues.text
    assert rastros.hallazgos() == []
    registros = texto_de_registros(caplog.records)
    for marca in marcas:
        assert marca not in registros
    assert ficha not in registros


def test_p_001_92_una_interaccion_antes_de_los_45_minutos_mantiene_abierta_la_sesion() -> None:
    """P-001-92 · NFR-000-17: la actividad de la persona reinicia la cuenta."""
    with _servicio() as (cliente, reloj, almacen):
        ficha = ficha_de(cargar(cliente, fixture("marcadores.xlsx"), NOMBRE_CON_MARCADOR))
        reloj.avanzar(minutes=44, seconds=59)
        assert enviar_a_sesion(cliente, RUTA_LATIDO, ficha).status_code == 204
        reloj.avanzar(minutes=44, seconds=59)
        purgadas = _purgar(almacen, reloj)
        abierta = _abre(cliente, ficha)

    assert purgadas == 0
    assert abierta


def test_p_001_92_las_rutas_de_sesion_no_dejan_la_ficha_ni_el_nombre_en_los_registros(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """P-001-92 · NFR-000-17, M14: descartar, latido y cierre no registran cuerpos ni cabeceras."""
    caplog.set_level(logging.DEBUG)
    with _servicio() as (cliente, reloj, almacen):
        ficha = ficha_de(cargar(cliente, fixture("marcadores.xlsx"), NOMBRE_CON_MARCADOR))
        enviar_a_sesion(cliente, RUTA_LATIDO, ficha)
        enviar_a_sesion(cliente, RUTA_CIERRE, ficha)
        enviar_a_sesion(cliente, RUTA_DESCARTAR, ficha)

    registros = texto_de_registros(caplog.records)
    assert ficha not in registros
    assert NOMBRE_CON_MARCADOR not in registros


# --- P-001-95: las sesiones son independientes -----------------------------------------------


def _dos_sesiones(cliente: Any) -> tuple[str, str]:
    ficha_a = _ficha(cliente, "sesion_a.xlsx")
    ficha_b = _ficha(cliente, "sesion_b.xlsx")
    assert ficha_a != ficha_b
    return ficha_a, ficha_b


def _b_intacta(cliente: Any, ficha_b: str) -> None:
    """La sesión B sigue mostrando su matriz, sin mensajes de fin de sesión ni nada de A."""
    texto = _texto(resultado(cliente, ficha_b))
    assert cabecera_esperada("sesion_b.xlsx", 8, "25 de noviembre de 2026") in texto
    assert "sesion_a.xlsx" not in texto
    assert E8_DESCARTE not in texto
    assert E8_INACTIVIDAD not in texto


def test_p_001_95_descartar_una_sesion_no_afecta_a_la_otra() -> None:
    """P-001-95 · NFR-000-18, SC-000-18 (fin): descartar A deja B abierta."""
    with _servicio() as (cliente, _reloj, almacen):
        ficha_a, ficha_b = _dos_sesiones(cliente)
        enviar_a_sesion(cliente, RUTA_DESCARTAR, ficha_a)
        cantidad = almacen.cantidad()
        _b_intacta(cliente, ficha_b)
        a_despues = resultado(cliente, ficha_a)

    assert cantidad == 1
    assert not hay_resultados(_texto(a_despues))


def test_p_001_95_cerrar_la_pestana_de_una_sesion_no_afecta_a_la_otra() -> None:
    """P-001-95 · NFR-000-18: el aviso de cierre de A no toca a B."""
    with _servicio() as (cliente, reloj, almacen):
        ficha_a, ficha_b = _dos_sesiones(cliente)
        enviar_a_sesion(cliente, RUTA_CIERRE, ficha_a)
        reloj.avanzar(seconds=10)
        purgadas = _purgar(almacen, reloj)
        _b_intacta(cliente, ficha_b)

    assert purgadas == 1
    assert almacen.obtener(ficha_a) is None


def test_p_001_95_la_inactividad_de_una_sesion_no_afecta_a_la_otra() -> None:
    """P-001-95 · NFR-000-17, NFR-000-18: cada sesión mide sus propios 45 minutos."""
    with _servicio() as (cliente, reloj, almacen):
        ficha_a = _ficha(cliente, "sesion_a.xlsx")
        reloj.avanzar(minutes=30)
        ficha_b = _ficha(cliente, "sesion_b.xlsx")
        reloj.avanzar(minutes=15)
        purgadas_a = _purgar(almacen, reloj)
        b_sigue = almacen.obtener(ficha_b) is not None
        reloj.avanzar(minutes=29, seconds=59)
        b_sigue_despues = almacen.obtener(ficha_b) is not None
        reloj.avanzar(seconds=1)
        purgadas_b = _purgar(almacen, reloj)

    assert purgadas_a == 1
    assert b_sigue
    assert b_sigue_despues
    assert purgadas_b == 1
    assert almacen.obtener(ficha_a) is None


def test_p_001_95_el_latido_de_una_sesion_no_extiende_a_la_otra() -> None:
    """P-001-95 · NFR-000-17, NFR-000-18: el latido de A no reinicia la cuenta de B."""
    with _servicio() as (cliente, reloj, almacen):
        ficha_a, ficha_b = _dos_sesiones(cliente)
        reloj.avanzar(minutes=44)
        enviar_a_sesion(cliente, RUTA_LATIDO, ficha_a)
        reloj.avanzar(minutes=1)
        purgadas = _purgar(almacen, reloj)
        a_sigue = almacen.obtener(ficha_a) is not None
        b_sigue = almacen.obtener(ficha_b) is not None

    assert purgadas == 1
    assert a_sigue
    assert not b_sigue


def test_p_001_95_e8_de_inactividad_solo_lo_recibe_la_ficha_que_termino() -> None:
    """P-001-95 · NFR-000-18: E8 de inactividad solo lo recibe la ficha que terminó."""
    with _servicio() as (cliente, reloj, almacen):
        ficha_a = _ficha(cliente, "sesion_a.xlsx")
        reloj.avanzar(minutes=44)
        ficha_b = _ficha(cliente, "sesion_b.xlsx")
        reloj.avanzar(minutes=1)
        _purgar(almacen, reloj)
        sin_ficha = cliente.get("/vista/inicio")
        con_b = resultado(cliente, ficha_b)
        con_a = resultado(cliente, ficha_a)

    assert E8_INACTIVIDAD not in _texto(sin_ficha)
    assert E8_INACTIVIDAD not in _texto(con_b)
    assert hay_resultados(_texto(con_b))
    assert E8_INACTIVIDAD in _texto(con_a)


def test_p_001_95_descartar_con_la_ficha_de_una_no_toca_a_la_otra_aunque_se_repita() -> None:
    """P-001-95 · NFR-000-18: descartar dos veces con la ficha de A deja a B intacta."""
    with _servicio() as (cliente, _reloj, _almacen):
        ficha_a, ficha_b = _dos_sesiones(cliente)
        enviar_a_sesion(cliente, RUTA_DESCARTAR, ficha_a)
        enviar_a_sesion(cliente, RUTA_DESCARTAR, ficha_a)
        enviar_a_sesion(cliente, RUTA_LATIDO, ficha_a)
        enviar_a_sesion(cliente, RUTA_CIERRE, ficha_a)
        _b_intacta(cliente, ficha_b)
