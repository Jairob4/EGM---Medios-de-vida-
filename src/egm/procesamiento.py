"""M13 `egm.procesamiento`: la fachada del núcleo (arquitectura §5 y §6.1, M13).

`procesar` es el único punto que la capa web y los futuros analizadores necesitan conocer: recibe
los bytes de la matriz, el nombre del archivo tal como llegó y la fecha de lectura, y devuelve un
único resultado inmutable. Encadena, todo en memoria y sobre los bytes recibidos:

1. `egm.archivo.validar_archivo` (M02): tamaño, tipo y contenido descomprimido declarado. Un
   rechazo termina la lectura, sin abrir el libro (NFR-000-19).
2. `egm.libro.abrir` (M03): el libro en memoria, de solo lectura. Cualquier excepción al abrir es
   un archivo dañado: `Rechazo("tipo")` (NC-ARQ-1; incluye el XML partido y la parte que se
   descomprime a más de lo declarado).
3. `egm.esquema.descubrir` (M04): un `FalloContrato` termina la lectura y es todo lo que se
   devuelve, sin corpus, conteos ni verificación (FR-001-02, FR-001-29).
4. `egm.lectura.leer` (M05): los documentos y sus advertencias por fila.
5. `egm.verificacion.verificar` (M08): la verificación cruzada con la hoja `EGM`.
6. Se arma `ResultadoLectura` con la identificación (nombre y fecha dados), el esquema, el corpus,
   las advertencias (primero las de verificación, después las del esquema y las del corpus; ADR-002,
   punto 5) y las notas.

Determinismo (NFR-000-09): este módulo nunca lee el reloj ni el entorno; la fecha de lectura la
inyecta quien llama. Con los mismos bytes y el mismo nombre, el resultado solo cambia en la fecha.

Reglas del núcleo (arquitectura §4.1): importa los demás módulos del núcleo; no importa la capa web
ni la biblioteca de lectura de libros; sin estado global y sin entrada ni salida. Los módulos se
llaman por su espacio de nombres (`libro.abrir`, `lectura.leer`) para que las pruebas puedan
comprobar qué etapas corren.
"""

from datetime import datetime

from egm import archivo, esquema, lectura, libro, verificacion
from egm.modelo import FalloContrato, Identificacion, Rechazo, ResultadoLectura

__all__ = ["procesar"]


def procesar(
    contenido: bytes, nombre_archivo: str, fecha_lectura: datetime
) -> ResultadoLectura | Rechazo | FalloContrato:
    """Lee y verifica una matriz bibliográfica a partir de sus bytes.

    - `contenido`: los bytes del archivo `.xlsx`; no se escriben ni se guardan.
    - `nombre_archivo`: el nombre tal como llegó; se conserva sin cambios en la identificación.
    - `fecha_lectura`: la fecha de lectura, dada por quien llama; nunca se lee el reloj.

    Devuelve un `Rechazo` si el archivo no se puede leer (tipo, tamaño o contenido), un
    `FalloContrato` si la matriz incumple el contrato (y nada más: sin resultados parciales) o un
    `ResultadoLectura` completo. No lanza excepciones por el contenido del archivo.
    """
    rechazo = archivo.validar_archivo(contenido)
    if rechazo is not None:
        return rechazo

    try:
        abierto = libro.abrir(contenido)
    except Exception:  # límite del módulo: todo fallo al abrir es un archivo dañado (NC-ARQ-1)
        return Rechazo("tipo")

    descubierto = esquema.descubrir(abierto)
    if isinstance(descubierto, FalloContrato):
        return descubierto

    corpus = lectura.leer(abierto, descubierto)
    verificada = verificacion.verificar(abierto, descubierto, corpus)

    return ResultadoLectura(
        identificacion=Identificacion(nombre_archivo=nombre_archivo, fecha_lectura=fecha_lectura),
        esquema=descubierto,
        corpus=corpus,
        advertencias=(*verificada.advertencias, *descubierto.advertencias, *corpus.advertencias),
        notas=descubierto.notas,
        verificacion=verificada,
    )
