"""M15 `app.sesiones`: el almacén de sesiones en memoria (arquitectura §6.2, M15; ADR-003, punto 4).

Cada sesión guarda el `ResultadoLectura` de una matriz y la hora de su última actividad, bajo una
ficha aleatoria de 256 bits. Nada va a disco. Ninguna sesión ve otra: se llega a una sesión solo
con su ficha, y una ficha que no existe no abre nada.

Una sesión termina de cuatro formas (NFR-000-17): al descartar el archivo, al cerrar la pestaña,
tras 45 minutos sin actividad o con un error de contrato en una carga nueva.

- Inactividad: los 45 minutos se miden desde la última actividad (el último latido o petición con
  la ficha, ADR-003 punto 5). Con 44 min 59 s la sesión sigue; con 45 min se purga.
- Cierre de pestaña: el aviso de cierre no termina la sesión; la deja marcada, y pasados 10 s sin
  que la misma ficha vuelva (una recarga) la purga (ADR-003, punto 9). Cualquier actividad con la
  ficha anula el aviso.
- Una sesión vencida no se sirve aunque la tarea de purga aún no haya corrido: `obtener` y
  `registrar_actividad` la purgan al mirarla.
- Para decir «La sesión terminó porque pasaron 45 minutos…» (E8) se recuerda, solo la ficha y sin
  ningún dato de la matriz, que esa ficha terminó por inactividad; el recuerdo se entrega una vez
  y no pasa de `_MAXIMO_DE_RECUERDOS` fichas.

El filtro aplicado llega con el plan 002 (`aplicar_filtro`): `reemplazar` ya lo deja vacío,
porque arma una sesión nueva solo con el resultado (FR-001-29).
"""

import secrets
from collections.abc import Callable
from dataclasses import dataclass, replace
from datetime import datetime, timedelta
from enum import StrEnum
from typing import Final

from egm.modelo import ResultadoLectura

__all__ = [
    "CABECERA_SESION",
    "AVISO_INACTIVIDAD",
    "GRACIA_CIERRE",
    "INACTIVIDAD",
    "AlmacenSesiones",
    "CausaFin",
    "Sesion",
]

CABECERA_SESION: Final = "X-EGM-Sesion"
"""Cabecera con la ficha de sesión: en cada petición (ADR-003, punto 4) y, con la ficha nueva, en
la respuesta de la carga (plan 001, tabla de rutas). Nunca una cookie."""

INACTIVIDAD: Final = timedelta(minutes=45)
"""NFR-000-17: la sesión termina tras 45 minutos sin actividad. Fijo, no configurable."""

AVISO_INACTIVIDAD: Final = timedelta(minutes=43)
"""Flujos §2, E7: el aviso de fin de sesión sale a los 43 minutos sin actividad (WCAG 2.2.1)."""

GRACIA_CIERRE: Final = timedelta(seconds=10)
"""ADR-003, punto 9: espera tras el aviso de cierre de pestaña antes de borrar. Fijo."""

_BYTES_DE_LA_FICHA: Final = 32  # 256 bits
_MAXIMO_DE_RECUERDOS: Final = 256


class CausaFin(StrEnum):
    """Por qué termina una sesión (NFR-000-17)."""

    DESCARTE = "descarte"
    CIERRE_DE_PESTANA = "cierre_de_pestana"
    INACTIVIDAD = "inactividad"
    ERROR_DE_CONTRATO = "error_de_contrato"


@dataclass(frozen=True, slots=True)
class Sesion:
    """Lo que guarda una sesión: el resultado de la lectura y la hora de su última actividad."""

    resultado: ResultadoLectura
    ultima_actividad: datetime


class AlmacenSesiones:
    """Almacén en memoria. Un solo proceso: el estado vive en este objeto (ADR-003, punto 1)."""

    def __init__(self, reloj: Callable[[], datetime]) -> None:
        self._reloj = reloj
        self._sesiones: dict[str, Sesion] = {}
        self._avisos_de_cierre: dict[str, datetime] = {}
        self._terminadas_por_inactividad: dict[str, None] = {}

    def cantidad(self) -> int:
        """Cuántas sesiones guarda el almacén en este momento (sin purgar ninguna)."""
        return len(self._sesiones)

    def crear(self, resultado: ResultadoLectura) -> str:
        """Abre una sesión con el resultado y devuelve su ficha (aleatoria, de 256 bits)."""
        ficha = secrets.token_urlsafe(_BYTES_DE_LA_FICHA)
        while ficha in self._sesiones:  # nunca pasa en la práctica; sin ello no habría garantía
            ficha = secrets.token_urlsafe(_BYTES_DE_LA_FICHA)
        self._sesiones[ficha] = Sesion(resultado, self._reloj())
        return ficha

    def reemplazar(self, ficha: str, resultado: ResultadoLectura) -> None:
        """Cambia el resultado de la sesión por el nuevo y deja vacío el filtro aplicado.

        La ficha sigue siendo la misma. Si no hay sesión con esa ficha no hace nada (la sesión
        pudo terminar mientras se leía el archivo nuevo): quien llama debe haberla comprobado.
        """
        if ficha in self._sesiones:
            self._sesiones[ficha] = Sesion(resultado, self._reloj())
            self._avisos_de_cierre.pop(ficha, None)

    def obtener(self, ficha: str) -> Sesion | None:
        """La sesión de esa ficha, o `None` si no existe o ya terminó.

        Una sesión vencida (45 minutos sin actividad, o 10 s tras el aviso de cierre) termina aquí
        mismo si la purga periódica aún no la alcanzó. No cuenta como actividad.
        """
        sesion = self._sesiones.get(ficha)
        if sesion is None:
            return None
        causa = self._causa_de_vencimiento(ficha, sesion, self._reloj())
        if causa is not None:
            self.terminar(ficha, causa)
            return None
        return sesion

    def registrar_actividad(self, ficha: str) -> bool:
        """Cuenta una actividad (latido o petición con la ficha): reinicia los 45 minutos y anula
        un aviso de cierre pendiente (la ficha volvió). Devuelve si la ficha abre una sesión."""
        sesion = self.obtener(ficha)
        if sesion is None:
            return False
        self._sesiones[ficha] = replace(sesion, ultima_actividad=self._reloj())
        self._avisos_de_cierre.pop(ficha, None)
        return True

    def avisar_cierre(self, ficha: str) -> None:
        """La pestaña avisa que se cierra: la sesión se purga pasada `GRACIA_CIERRE` si la ficha no
        vuelve. No cuenta como actividad. Una ficha que no abre nada no hace nada."""
        if self.obtener(ficha) is not None:
            self._avisos_de_cierre[ficha] = self._reloj()

    def terminar(self, ficha: str, causa: CausaFin) -> None:
        """Termina la sesión y suelta su resultado: ya no se puede abrir con esa ficha.

        De la matriz no se guarda nada. Si la causa es la inactividad se recuerda solo la ficha,
        para poder decirle a esa pestaña por qué terminó (`consumir_fin_por_inactividad`).
        Terminar una ficha que no existe no hace nada.
        """
        if self._sesiones.pop(ficha, None) is None:
            return
        self._avisos_de_cierre.pop(ficha, None)
        if causa is CausaFin.INACTIVIDAD:
            self._terminadas_por_inactividad[ficha] = None
            while len(self._terminadas_por_inactividad) > _MAXIMO_DE_RECUERDOS:
                del self._terminadas_por_inactividad[next(iter(self._terminadas_por_inactividad))]

    def consumir_fin_por_inactividad(self, ficha: str) -> bool:
        """Si esa ficha terminó por inactividad y nadie lo ha dicho aún; solo se dice una vez."""
        return self._terminadas_por_inactividad.pop(ficha, 0) is None

    def purgar_vencidas(self, ahora: datetime) -> int:
        """Termina las sesiones vencidas a la hora `ahora` y devuelve cuántas fueron."""
        vencidas = [
            (ficha, causa)
            for ficha, sesion in self._sesiones.items()
            if (causa := self._causa_de_vencimiento(ficha, sesion, ahora)) is not None
        ]
        for ficha, causa in vencidas:
            self.terminar(ficha, causa)
        return len(vencidas)

    def _causa_de_vencimiento(self, ficha: str, sesion: Sesion, ahora: datetime) -> CausaFin | None:
        if ahora - sesion.ultima_actividad >= INACTIVIDAD:
            return CausaFin.INACTIVIDAD
        aviso = self._avisos_de_cierre.get(ficha)
        if aviso is not None and ahora - aviso >= GRACIA_CIERRE:
            return CausaFin.CIERRE_DE_PESTANA
        return None
