"""Pruebas P-001-03 y P-001-04 de M01 `egm.modelo` (plan 001, T-001-10).

Todos los esperados están escritos a mano a partir de la arquitectura §6.1 (M01), del contrato de
datos y de los requisitos NFR-000-02, FR-001-11 y NFR-000-09. No hay fixtures: los valores van en
la prueba.
"""

import dataclasses
import inspect
import re
from datetime import UTC, datetime, timedelta, timezone
from enum import Enum
from typing import Any, get_args, get_type_hints

import pytest

from egm import modelo
from egm.modelo import (
    SIN_NIVEL,
    Advertencia,
    Anclas,
    AnioNoReconocido,
    Conteo,
    Corpus,
    DatosCrudos,
    Documento,
    Enfoque,
    ErrorContrato,
    Esquema,
    EstadoDocumento,
    FalloContrato,
    Identificacion,
    Lista,
    Nota,
    Rechazo,
    RefFila,
    ResultadoLectura,
    Rol,
)

# --------------------------------------------------------------------------------------------
# P-001-03 · NFR-000-02, FR-001-11: un número es la longitud de su lista de filas
# --------------------------------------------------------------------------------------------


def _filas(*filas: int) -> tuple[RefFila, ...]:
    return tuple(RefFila(numero=str(f - 1), fila=f) for f in filas)


@pytest.mark.parametrize(
    ("filas", "esperado"),
    [
        ((), 0),
        ((2,), 1),
        ((2, 5, 9), 3),
        ((2, 3, 4, 5, 6, 7, 8, 9, 10, 11), 10),
    ],
)
def test_el_valor_del_conteo_es_la_longitud_de_sus_filas(
    filas: tuple[int, ...], esperado: int
) -> None:
    """P-001-03 (NFR-000-02, FR-001-11): `Conteo.valor == len(filas)`."""
    conteo = Conteo(filas=_filas(*filas))
    assert conteo.valor == esperado
    assert len(conteo.filas) == esperado


def test_las_filas_se_conservan_en_el_orden_del_archivo() -> None:
    """P-001-03 (FR-001-11): las filas quedan en el orden del archivo, con su N.º y su fila."""
    filas = (
        RefFila(numero="3", fila=4),
        RefFila(numero=None, fila=7),
        RefFila(numero="12", fila=15),
    )
    conteo = Conteo(filas=filas)
    assert conteo.filas == filas
    assert [r.fila for r in conteo.filas] == [4, 7, 15]
    assert [r.numero for r in conteo.filas] == ["3", None, "12"]


def test_un_conteo_rechaza_filas_repetidas() -> None:
    """P-001-03 (FR-001-11): sin repetidos; un documento cuenta una sola vez."""
    with pytest.raises(ValueError, match="repet"):
        Conteo(filas=_filas(2, 5, 5))
    with pytest.raises(ValueError, match="repet"):
        Conteo(filas=(RefFila(numero="1", fila=2), RefFila(numero="1", fila=2)))


def test_un_conteo_rechaza_filas_fuera_del_orden_del_archivo() -> None:
    """P-001-03 (FR-001-11): el orden del archivo es el de la fila, de menor a mayor."""
    with pytest.raises(ValueError, match="orden"):
        Conteo(filas=_filas(5, 2))
    with pytest.raises(ValueError, match="orden"):
        Conteo(filas=_filas(2, 9, 4))


def test_un_conteo_toma_una_copia_inmutable_de_las_filas() -> None:
    """P-001-03 (NFR-000-02): la lista de origen no puede alterar el conteo después."""
    origen = [RefFila(numero="1", fila=2), RefFila(numero="2", fila=3)]
    conteo = Conteo(filas=origen)  # type: ignore[arg-type]
    origen.append(RefFila(numero="3", fila=4))
    assert isinstance(conteo.filas, tuple)
    assert conteo.valor == 2


def test_no_hay_otro_modo_de_crear_un_numero() -> None:
    """P-001-03 (NFR-000-02): solo entra `filas`; `valor` no se pasa ni se asigna."""
    parametros = list(inspect.signature(Conteo).parameters)
    assert parametros == ["filas"]
    assert [campo.name for campo in dataclasses.fields(Conteo)] == ["filas"]
    assert isinstance(Conteo.valor, property)
    assert Conteo.valor.fset is None

    with pytest.raises(TypeError):
        Conteo(filas=_filas(2), valor=5)  # type: ignore[call-arg]
    with pytest.raises(TypeError):
        Conteo(valor=5)  # type: ignore[call-arg]

    conteo = Conteo(filas=_filas(2, 3))
    with pytest.raises(AttributeError):
        conteo.valor = 99  # type: ignore[misc]
    with pytest.raises(AttributeError):
        conteo.filas = ()  # type: ignore[misc]
    assert conteo.valor == 2


def test_dos_conteos_con_las_mismas_filas_son_iguales() -> None:
    """P-001-03 (NFR-000-02): la igualdad es la de la lista de filas (misma lista, mismo número)."""
    assert Conteo(filas=_filas(2, 3)) == Conteo(filas=_filas(2, 3))
    assert Conteo(filas=_filas(2, 3)) != Conteo(filas=_filas(2, 4))
    assert hash(Conteo(filas=_filas(2, 3))) == hash(Conteo(filas=_filas(2, 3)))


# --------------------------------------------------------------------------------------------
# P-001-04 · NFR-000-09: los tipos de M01 son inmutables; la identificación guarda lo recibido
# --------------------------------------------------------------------------------------------


def _esquema() -> Esquema:
    return Esquema(
        columnas={Rol.IDENTIFICADOR: 0, Rol.REFERENCIA: 1},
        dimensiones=("Dim uno", "Dim dos"),
        intervenciones=("Int A", "Int B"),
        niveles=("Nivel 1",),
        tipos_documento=Lista(valores=("Tipo uno",), origen="validacion"),
        tipos_fuente=Lista(valores=("Fuente uno",), origen="presentes"),
        metodologias=Lista(valores=(), origen="presentes"),
        anclas=Anclas(empiricos=("Tipo uno",), evaluacion_impacto=None),
        advertencias=(),
        notas=(),
    )


def _documento() -> Documento:
    return Documento(
        ref=RefFila(numero="1", fila=2),
        anio=2020,
        tipo_documento="Tipo uno",
        tipo_fuente=None,
        metodologia=None,
        intervenciones=("Int A",),
        dimensiones=("Dim uno",),
        nivel=SIN_NIVEL,
        enfoque=Enfoque.SIN_DILIGENCIAR,
        estado=EstadoDocumento.EMPIRICO_PENDIENTE,
        textos={Rol.REFERENCIA: "Ref", Rol.HALLAZGOS: None},
        crudos=DatosCrudos(),
    )


def _corpus() -> Corpus:
    return Corpus(documentos=(_documento(),), advertencias=(), fila_final_leida=2)


class _Verificacion:
    """Doble mínimo de la `Verificacion` de M08 (aquí solo se necesita la forma común)."""

    def __init__(self) -> None:
        self.verificadas: tuple[int, ...] = (1, 2)
        self.advertencias: tuple[Advertencia, ...] = ()


def _instancias() -> dict[str, Any]:
    fecha = datetime(2026, 11, 21, 9, 30, tzinfo=UTC)
    return {
        "RefFila": RefFila(numero="1", fila=2),
        "Conteo": Conteo(filas=_filas(2, 3)),
        "Advertencia": Advertencia(
            codigo="x",
            ambito="fila",
            ref=RefFila(numero="1", fila=2),
            columna="Año",
            valor="dos mil",
            datos={"a": 1},
        ),
        "Nota": Nota(codigo="n", datos={"b": 2}),
        "ErrorContrato": ErrorContrato(codigo="e", esperado=("a",), encontrado=("b",)),
        "Identificacion": Identificacion(nombre_archivo="matriz.xlsx", fecha_lectura=fecha),
        "Rechazo": Rechazo(motivo="tipo"),
        "FalloContrato": FalloContrato(
            errores=(ErrorContrato(codigo="e", esperado=(), encontrado=()),)
        ),
        "Lista": Lista(valores=("a", "b"), origen="validacion"),
        "Anclas": Anclas(empiricos=("a",), evaluacion_impacto="b"),
        "AnioNoReconocido": AnioNoReconocido(texto="s. f."),
        "DatosCrudos": DatosCrudos(),
        "Esquema": _esquema(),
        "Documento": _documento(),
        "Corpus": _corpus(),
        "ResultadoLectura": ResultadoLectura(
            identificacion=Identificacion(nombre_archivo="m.xlsx", fecha_lectura=fecha),
            esquema=_esquema(),
            corpus=_corpus(),
            advertencias=(),
            notas=(),
            verificacion=_Verificacion(),
        ),
    }


def test_todos_los_tipos_de_m01_son_dataclasses_inmutables() -> None:
    """P-001-04 (NFR-000-09): ningún tipo de M01 deja asignar ni agregar atributos."""
    instancias = _instancias()
    assert len(instancias) == 16
    for nombre, instancia in instancias.items():
        assert dataclasses.is_dataclass(instancia), nombre
        params = type(instancia).__dataclass_params__  # type: ignore[attr-defined]
        assert params.frozen, nombre
        primer_campo = dataclasses.fields(instancia)
        with pytest.raises(AttributeError):
            setattr(instancia, "atributo_nuevo", 1)  # noqa: B010
        if primer_campo:
            with pytest.raises(dataclasses.FrozenInstanceError):
                setattr(instancia, primer_campo[0].name, None)


def test_los_campos_de_cada_tipo_son_los_de_la_arquitectura() -> None:
    """P-001-04 (NFR-000-09): campos de M01 según arquitectura §6.1, sin otros."""

    def nombres(tipo: type) -> list[str]:
        return [campo.name for campo in dataclasses.fields(tipo)]

    assert nombres(RefFila) == ["numero", "fila"]
    assert nombres(Conteo) == ["filas"]
    assert nombres(Advertencia) == ["codigo", "ambito", "ref", "columna", "valor", "datos"]
    assert nombres(Nota) == ["codigo", "datos"]
    assert nombres(ErrorContrato) == ["codigo", "esperado", "encontrado"]
    assert nombres(Identificacion) == ["nombre_archivo", "fecha_lectura"]
    assert nombres(ResultadoLectura) == [
        "identificacion",
        "esquema",
        "corpus",
        "advertencias",
        "notas",
        "verificacion",
    ]
    assert nombres(Rechazo) == ["motivo"]
    assert nombres(FalloContrato) == ["errores"]
    assert nombres(Esquema) == [
        "columnas",
        "dimensiones",
        "intervenciones",
        "niveles",
        "tipos_documento",
        "tipos_fuente",
        "metodologias",
        "anclas",
        "advertencias",
        "notas",
    ]
    assert nombres(Corpus) == ["documentos", "advertencias", "fila_final_leida"]
    assert nombres(Documento) == [
        "ref",
        "anio",
        "tipo_documento",
        "tipo_fuente",
        "metodologia",
        "intervenciones",
        "dimensiones",
        "nivel",
        "enfoque",
        "estado",
        "textos",
        "crudos",
    ]
    assert nombres(Lista) == ["valores", "origen"]


def test_identificacion_guarda_el_nombre_tal_como_llego_y_la_fecha_dada() -> None:
    """P-001-04 (NFR-000-09): el nombre no se normaliza ni se recorta; la fecha es la recibida."""
    zona = timezone(timedelta(hours=-5))
    casos = [
        ("Matriz EGM v4 (copia).xlsx", datetime(2026, 11, 21, 8, 5, 3, tzinfo=zona)),
        ("  MATRIZ_Año_ñ .XLSX ", datetime(2026, 1, 2, 3, 4, 5)),
        ("carpeta\\sub/otro.xlsx", datetime(2026, 12, 6, 23, 59, 59, 999999, tzinfo=UTC)),
        ("", datetime(2000, 2, 29)),
    ]
    for nombre, fecha in casos:
        identificacion = Identificacion(nombre_archivo=nombre, fecha_lectura=fecha)
        assert identificacion.nombre_archivo == nombre
        assert identificacion.fecha_lectura == fecha
        assert identificacion.fecha_lectura is fecha
        assert identificacion.fecha_lectura.tzinfo is fecha.tzinfo


def test_los_mapeos_de_los_tipos_quedan_de_solo_lectura() -> None:
    """P-001-04 (NFR-000-09): `datos`, `textos` y `columnas` no se pueden alterar desde afuera."""
    origen: dict[str, object] = {"clave": 1}
    advertencia = Advertencia(
        codigo="x", ambito="fila", ref=None, columna=None, valor=None, datos=origen
    )
    nota = Nota(codigo="n", datos=origen)
    origen["clave"] = 2
    origen["otra"] = 3
    assert dict(advertencia.datos) == {"clave": 1}
    assert dict(nota.datos) == {"clave": 1}
    with pytest.raises(TypeError):
        advertencia.datos["clave"] = 5  # type: ignore[index]
    with pytest.raises(TypeError):
        nota.datos["nueva"] = 5  # type: ignore[index]

    documento = _documento()
    with pytest.raises(TypeError):
        documento.textos[Rol.APORTE] = "x"  # type: ignore[index]
    esquema = _esquema()
    with pytest.raises(TypeError):
        esquema.columnas[Rol.ANIO] = 3  # type: ignore[index]


def test_advertencia_y_nota_se_comparan_por_valor() -> None:
    """P-001-04 (NFR-000-09): mismos datos, mismo resultado; igualdad por valor."""
    a = Advertencia(codigo="x", ambito="fila", ref=None, columna="c", valor="v", datos={"k": 1})
    b = Advertencia(codigo="x", ambito="fila", ref=None, columna="c", valor="v", datos={"k": 1})
    c = Advertencia(codigo="x", ambito="fila", ref=None, columna="c", valor="v", datos={"k": 2})
    assert a == b
    assert a != c
    assert Nota(codigo="n", datos={}) == Nota(codigo="n", datos={})


def test_los_enumerados_tienen_los_miembros_de_la_arquitectura() -> None:
    """P-001-04 (FR-001-13, FR-001-10): estados y categorías de enfoque del contrato."""
    assert issubclass(EstadoDocumento, Enum)
    assert [m.name for m in EstadoDocumento] == [
        "EN_EL_MAPA",
        "EMPIRICO_PENDIENTE",
        "NO_EMPIRICO",
        "SIN_TIPO_VALIDO",
    ]
    assert issubclass(Enfoque, Enum)
    assert [m.name for m in Enfoque] == [
        "SI",
        "NO",
        "PARCIAL",
        "SIN_CLASIFICAR",
        "SIN_DILIGENCIAR",
    ]
    assert len({m.value for m in EstadoDocumento}) == 4
    assert len({m.value for m in Enfoque}) == 5


def test_roles_de_columna_son_los_del_contrato() -> None:
    """P-001-04 (contrato §3): un rol por fila de la tabla de roles, sin más."""
    assert [m.name for m in Rol] == [
        "IDENTIFICADOR",
        "REFERENCIA",
        "ANIO",
        "TIPO_DOCUMENTO",
        "PAIS_POBLACION",
        "TIPO_FUENTE",
        "INTERVENCION_PRINCIPAL",
        "INTERVENCION_SECUNDARIA",
        "METODOLOGIA",
        "NIVEL_EVIDENCIA",
        "DELIMITADOR_INICIAL",
        "DELIMITADOR_FINAL",
        "ENFOQUE",
        "HALLAZGOS",
        "VACIO",
        "LIMITACIONES",
        "APORTE",
    ]


def test_sin_nivel_es_una_entrada_distinta_de_cualquier_nivel_vacio() -> None:
    """P-001-04 (FR-002-12): la entrada «Sin nivel» es un valor fijo y no vacío."""
    assert SIN_NIVEL == "Sin nivel"
    assert isinstance(SIN_NIVEL, str)


def test_rechazo_admite_los_tres_motivos_de_la_arquitectura() -> None:
    """P-001-04 (FR-001-29): motivo "tipo", "tamano" o "contenido"."""
    motivo = get_type_hints(Rechazo)["motivo"]
    assert set(get_args(motivo)) == {"tipo", "tamano", "contenido"}
    for valor in ("tipo", "tamano", "contenido"):
        assert Rechazo(motivo=valor).motivo == valor  # type: ignore[arg-type]


def test_fallo_de_contrato_conserva_los_errores_en_orden() -> None:
    """P-001-04 (NFR-000-09): los errores de contrato viajan como valor, en el orden dado."""
    e1 = ErrorContrato(codigo="falta_encabezado", esperado=("N°",), encontrado=())
    e2 = ErrorContrato(codigo="sin_hoja", esperado=("Matriz bibliográfica",), encontrado=("Hoja1",))
    fallo = FalloContrato(errores=(e1, e2))
    assert fallo.errores == (e1, e2)
    assert fallo.errores[1].esperado == ("Matriz bibliográfica",)
    assert fallo.errores[1].encontrado == ("Hoja1",)


# --------------------------------------------------------------------------------------------
# P-001-04 · FR-001-12, FR-001-02: lista cerrada de códigos de advertencia, nota y error
# --------------------------------------------------------------------------------------------

_NOMBRES_CODIGOS: tuple[str, ...] = (
    # Advertencias de fila (M05).
    "ENFOQUE_SIN_CLASIFICAR",
    "VALOR_FUERA_DE_LISTA",
    "ESPACIOS_EN_LOS_EXTREMOS",
    "DIMENSION_VALOR_INVALIDO",
    "ANIO_NO_RECONOCIDO",
    "NUMERO_VACIO",
    "NUMERO_REPETIDO",
    "PRINCIPAL_IGUAL_SECUNDARIA",
    "NO_EMPIRICO_CON_INTERVENCION",
    "TIPO_DOCUMENTO_FUERA_DE_LISTA",
    # Advertencias de estructura (M04).
    "BLOQUE_SIN_DIMENSIONES",
    "ROL_DENTRO_DEL_BLOQUE",
    "LISTA_1_0_FUERA_DEL_BLOQUE",
    "DIMENSION_SIN_LISTA_1_0",
    "LISTA_SIN_NO_APLICA",
    "VARIOS_EMPIRICOS",
    "SIN_ANCLA_EVALUACION_IMPACTO",
    "COLUMNA_SIN_LISTA",
    # Nota (M04).
    "COLUMNAS_NO_USADAS",
    # Errores de contrato (M04).
    "HOJA_AUSENTE",
    "ENCABEZADO_AUSENTE",
    "ANCLA_EMPIRICA_AUSENTE",
    "LISTA_OBLIGATORIA_AUSENTE",
)


def _todos_los_codigos() -> tuple[str, ...]:
    return (
        *modelo.CODIGOS_ADVERTENCIA_FILA,
        *modelo.CODIGOS_ADVERTENCIA_ESTRUCTURA,
        *modelo.CODIGOS_NOTA,
        *modelo.CODIGOS_ERROR_CONTRATO,
    )


def test_cada_codigo_es_una_cadena_en_snake_case() -> None:
    """P-001-04 (FR-001-12): cada código es `str` y cumple `^[a-z][a-z0-9_]*$`."""
    for codigo in _todos_los_codigos():
        assert isinstance(codigo, str), codigo
        assert re.fullmatch(r"[a-z][a-z0-9_]*", codigo), codigo


def test_no_hay_codigos_repetidos_entre_las_cuatro_tuplas() -> None:
    """P-001-04 (FR-001-12): los códigos de las cuatro tuplas son únicos."""
    codigos = _todos_los_codigos()
    assert len(codigos) == len(set(codigos))


def test_el_numero_de_codigos_por_tupla_es_el_de_la_lista_cerrada() -> None:
    """P-001-04 (FR-001-02): 10 advertencias de fila, 8 de estructura, 1 nota y 4 errores."""
    assert len(modelo.CODIGOS_ADVERTENCIA_FILA) == 10
    assert len(modelo.CODIGOS_ADVERTENCIA_ESTRUCTURA) == 8
    assert len(modelo.CODIGOS_NOTA) == 1
    assert len(modelo.CODIGOS_ERROR_CONTRATO) == 4


def test_cada_constante_vale_su_nombre_en_minusculas() -> None:
    """P-001-04 (FR-001-12): la constante `X` tiene el valor `"x"`, y las tuplas agrupan los 23."""
    for nombre in _NOMBRES_CODIGOS:
        assert getattr(modelo, nombre) == nombre.lower(), nombre
    assert sorted(_todos_los_codigos()) == sorted(n.lower() for n in _NOMBRES_CODIGOS)
    assert len(_NOMBRES_CODIGOS) == 23
