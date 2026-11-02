---
name: analisis-impacto
description: Método para medir el impacto de una corrección sobre todo el sistema EGM (specs, arquitectura, interfaz, planes, pruebas) y para comprobar la consistencia después de aplicarla. Usar al proponer o aplicar cualquier corrección.
---

# Análisis de impacto y consistencia

El sistema es una red de referencias: IDs, símbolos, términos, valores y decisiones. Corregir un nodo sin recorrer sus aristas es lo que rompe lo demás. Los invariantes que ninguna corrección puede alterar están en `references/invariantes.md`; léalo siempre.

## Antes de proponer

1. **Identifique el objetivo**: los IDs (`FR-`, `NFR-`, `US-`, `SC-`, `ADR-`, `COR-`), los símbolos (`$E$`, `$S(i,j)$`, `$T_1$`, `$T_2$`, `$T_4$`, `n_min`…), los términos (incluidos sus sinónimos) y los valores (cifras, nombres de estados, textos literales de la matriz) que el cambio toca.
2. **Búsqueda exhaustiva** con Grep en todo el repositorio de documentos y código (`docs/`, `src/`, `app/`, `tests/`): cada ID y cada término, con variantes de tilde y de mayúsculas. Un valor repetido (p. ej. una cifra o el nombre de un estado) se busca por su texto exacto.
3. **Clasifique cada coincidencia**: depende del significado, o solo lo menciona.
4. **Dependencias que no aparecen en una búsqueda**: escenarios cuyo resultado depende de la regla; SC que la miden; filas de `trazabilidad.md`; ADR que la motivan; pruebas y fixtures que la ejercen.
5. **Contraste con los invariantes** para cada opción, incluida la opción 0.
6. **Arme la matriz de impacto** de la plantilla: elemento, tipo, efecto, acción.

## Después de aplicar (verificación de consistencia)

Repita las búsquedas del paso 2 sobre el estado nuevo y responda:

- [ ] ¿Todos los IDs son únicos y no queda ninguna referencia a un ID inexistente?
- [ ] ¿Todo FR tiene al menos un escenario o SC, también tras el cambio?
- [ ] ¿Quedaron términos mezclados (advertencia/aviso, celda/casilla)?
- [ ] ¿Cada valor repetido dice lo mismo en todos sus lugares?
- [ ] ¿`trazabilidad.md` refleja los requisitos nuevos, cambiados o eliminados?
- [ ] ¿Se mantienen todos los invariantes?
- [ ] ¿Se tocaron únicamente los archivos de la sección 5 de la propuesta?

Registre cada respuesta con la evidencia de la búsqueda (qué se buscó y cuántas coincidencias salieron). Una respuesta sin evidencia no cuenta. El hash de `data/raw/` y el `git diff` los comprueba el `verificador`, que tiene los medios para hacerlo, en la auditoría única al cerrar el plan de corrección. Hasta entonces esta verificación es el único control de cada corrección: no la abrevie.
