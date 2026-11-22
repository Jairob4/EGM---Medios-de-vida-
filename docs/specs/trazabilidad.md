# Matriz de trazabilidad

Fuente → requisito → componente → tarea → prueba. Cada fase llena su columna; ninguna borra lo de la anterior.

**Estados** (skill `trazabilidad`): `especificado` → `diseñado` → `planificado` → `implementado` → `verificado`. Quién los cambia: a `diseñado`, COR-013 (arquitectura aprobada el 22-nov-2026); a `planificado`, la sesión principal, cuando Jairo aprueba los planes que citan el requisito en «Tarea»; a `implementado`, el `implementador`, en la tarea de cierre del último plan que tenga tareas del requisito; a `verificado`, la sesión principal, cuando el informe del `verificador` de ese plan no deja hallazgos abiertos sobre el requisito. La columna «Tarea» se llenó en la Fase 3 y solo cambia por una corrección; la columna «Prueba» la llena el `implementador`. Los criterios de revisión humana (SC-000-03, SC-003-05) se anotan en «Prueba» como «revisión manual (T-…)».

| Requisito | Fuente | Componente (ADR/arquitectura) | Tarea (plan) | Prueba | Estado |
|---|---|---|---|---|---|
| NFR-000-01 | doc. técnico §4.2 RNF1; decisión de Jairo, 2-nov-2026 | `egm.libro`, `app.carga` (ADR-001, ADR-004) | T-001-13, T-001-65, T-003-63 |  | diseñado |
| NFR-000-02 | doc. general §4.2; doc. técnico §4.2 RNF4 | `egm.modelo`, `egm.conteo`, `egm.conclusiones`, `app.presentacion` (ADR-001) | T-001-11, T-001-25, T-003-08, T-003-13, T-003-15, T-003-33, T-003-43 |  | diseñado |
| NFR-000-03 | estado §5 | `egm.textos`, `app.plantillas` | T-001-17, T-001-34, T-001-46, T-001-67, T-001-70, T-001-85, T-001-93, T-002-49, T-003-14, T-003-25, T-003-32, T-003-47, T-003-92 |  | diseñado |
| NFR-000-04 | prompt de la fase 1, T3 | `app.plantillas`, `app.cliente` (ADR-003) | T-001-67, T-001-68, T-001-84, T-001-85, T-002-04, T-002-15, T-002-24, T-002-25, T-002-32, T-002-37, T-002-44, T-002-45, T-003-16, T-003-27, T-003-35, T-003-49, T-003-57, T-003-62, T-003-90, T-003-91 |  | diseñado |
| NFR-000-05 | prompt de la fase 1, T3 | `app.plantillas` (ADR-003) | T-001-67, T-002-14, T-002-31, T-002-45, T-003-90, T-003-91 |  | diseñado |
| NFR-000-06 | doc. general §9; decisión de Jairo, 1-nov-2026; decisión de Jairo, 2-nov-2026 | `egm.esquema`, `egm.lectura`, `egm.conteo`, `tests.constructor`, `app.presentacion` (M17), `app.plantillas` (M18) (ADR-001) | T-001-04, T-001-23, T-001-24, T-002-02, T-002-13 |  | diseñado |
| NFR-000-07 | doc. general §7; decisión de Jairo, 1-nov-2026 | `egm.porcentajes`, `app.configuracion` | T-003-06, T-003-07, T-003-36 |  | diseñado |
| NFR-000-08 | doc. general §7; lámina 5 | `egm.textos`, `app.presentacion` | T-002-12, T-002-49, T-003-25, T-003-55 |  | diseñado |
| NFR-000-09 | doc. técnico §4.2 RNF2 | `egm.procesamiento`, `egm.modelo`, `app.presentacion`, `app.exportacion` (ADR-001) | T-001-11, T-001-51, T-002-39 |  | diseñado |
| NFR-000-10 | doc. técnico §4.2 RNF5 | `app.presentacion`, `app.plantillas` | T-002-13, T-002-14, T-002-45 |  | diseñado |
| NFR-000-11 | decisión de Jairo, 31-oct-2026; decisión de Jairo, 2-nov-2026 | `app.colofon`, `app.configuracion`, `app.plantillas` (ADR-005: bloques institucionales apagados por defecto) | T-001-62, T-001-63, T-001-67, T-001-94 |  | diseñado |
| NFR-000-12 | decisión de Jairo, 31-oct-2026; decisión de Jairo, 2-nov-2026; decisión de Jairo, 3-nov-2026 | `app.colofon`, `app.presentacion`, `egm.procesamiento` (ADR-005) | T-001-63, T-001-66 |  | diseñado |
| NFR-000-13 | decisión de Jairo, 31-oct-2026 | `app.plantillas` (ADR-003) | T-001-67, T-001-94, T-002-14, T-002-31, T-002-42, T-002-44, T-002-45, T-003-16, T-003-27, T-003-49, T-003-91 |  | diseñado |
| NFR-000-14 | decisión de Jairo, 31-oct-2026 | núcleo `egm.*` sin dependencias web; `egm.procesamiento`; puntos de extensión PE-1 a PE-7 (arquitectura §7) | T-001-01, T-001-02, T-001-51, T-001-52, T-002-48 |  | diseñado |
| NFR-000-15 | doc. general §4.2; decisión de Jairo, 31-oct-2026 | `app.servidor` (ADR-003, ADR-004) | T-001-02, T-001-69 |  | diseñado |
| NFR-000-16 | doc. general §3 | `app.colofon`, `app.plantillas` (ADR-005) | T-002-16 |  | diseñado |
| NFR-000-17 | decisión de Jairo, 2-nov-2026; decisión de Jairo, 3-nov-2026; decisión de Jairo, 21-nov-2026 | `app.sesiones`, `app.carga`, `app.cliente`, `app.servidor` (ADR-003, ADR-004) | T-001-64, T-001-65, T-001-68, T-001-69, T-001-82, T-001-83, T-001-84 |  | diseñado |
| NFR-000-18 | decisión de Jairo, 2-nov-2026 | `app.sesiones` (ADR-003) | T-001-64, T-001-82 |  | diseñado |
| NFR-000-19 | decisión de Jairo, 2-nov-2026; decisión de Jairo, 3-nov-2026; decisión de Jairo, 21-nov-2026 | `egm.archivo`, `app.carga` (ADR-003, ADR-004) | T-001-06, T-001-09, T-001-15, T-001-17, T-001-51, T-001-65 |  | diseñado |
| FR-001-01 | doc. técnico §5.1 | `egm.esquema`, `egm.libro` | T-001-13, T-001-23 |  | diseñado |
| FR-001-02 | doc. técnico §5.1, §5.3 | `egm.esquema`, `egm.textos` | T-001-32, T-001-34, T-001-51 |  | diseñado |
| FR-001-03 | decisión de Jairo, 1-nov-2026 | `egm.esquema` | T-001-23, T-001-32 |  | diseñado |
| FR-001-04 | decisión de Jairo, 1-nov-2026 | `egm.esquema` | T-001-32 |  | diseñado |
| FR-001-05 | doc. técnico §12.2 | `egm.libro`, `egm.esquema` (ADR-001) | T-001-05, T-001-13, T-001-23 |  | diseñado |
| FR-001-06 | doc. técnico §9.2 | `egm.lectura` (ADR-001) | T-001-24 |  | diseñado |
| FR-001-07 | Matriz Instrucciones B20; lámina 6; decisión de Jairo, 3-nov-2026 | `egm.conteo` (ADR-001) | T-001-25 |  | diseñado |
| FR-001-08 | doc. general §7 | `egm.conteo` (ADR-001) | T-001-25 |  | diseñado |
| FR-001-09 | doc. técnico §2.4 | `egm.conteo` (ADR-001) | T-001-25 |  | diseñado |
| FR-001-10 | Matriz Instrucciones B14; doc. técnico §6.6; decisión de Jairo, 2-nov-2026 | `egm.lectura`, `egm.textos` | T-001-24, T-001-33, T-001-34 |  | diseñado |
| FR-001-11 | doc. general §4.2 | `egm.modelo`, `egm.conteo` (ADR-001) | T-001-11, T-001-25 |  | diseñado |
| FR-001-12 | doc. técnico §9.2 | `egm.lectura`, `egm.esquema`, `egm.verificacion`, `egm.textos` | T-001-32, T-001-33, T-001-34, T-001-44, T-001-66, T-001-93 |  | diseñado |
| FR-001-13 | doc. técnico §9.2; decisión de Jairo, 2-nov-2026 | `egm.lectura`, `egm.conteo` | T-001-24, T-001-25, T-001-33 |  | diseñado |
| FR-001-14 | doc. general §4.1; doc. técnico §9.1 | `egm.verificacion`, `egm.conteo`, `tests.constructor` (ADR-002) | T-001-05, T-001-44 |  | diseñado |
| FR-001-15 | decisión de Jairo, 1-nov-2026 | `egm.verificacion` (ADR-002) | T-001-43 |  | diseñado |
| FR-001-16 | decisión de Jairo, 1-nov-2026 | `egm.verificacion` (ADR-002) | T-001-44 |  | diseñado |
| FR-001-17 | doc. técnico §9.1 | `egm.verificacion`, `egm.libro` (ADR-002) | T-001-13, T-001-44 |  | diseñado |
| FR-001-18 | doc. general §4.1; doc. técnico §3.2 | `egm.verificacion`, `egm.textos`, `app.presentacion` (ADR-002) | T-001-45, T-001-46, T-001-51, T-001-66 |  | diseñado |
| FR-001-19 | doc. técnico §4.2 RNF2 | `egm.procesamiento`, `app.presentacion` | T-001-51, T-001-66 |  | diseñado |
| FR-001-20 | decisión de Jairo, 2-nov-2026; decisión de Jairo, 3-nov-2026 | `app.carga`, `app.cliente`, `app.sesiones`, `egm.archivo` (ADR-004) | T-001-15, T-001-64, T-001-65, T-001-68 |  | diseñado |
| FR-001-21 | decisión de Jairo, 2-nov-2026 | `egm.esquema` | T-001-32, T-001-34 |  | diseñado |
| FR-001-22 | decisión de Jairo, 2-nov-2026 | `egm.esquema` | T-001-23, T-001-32 |  | diseñado |
| FR-001-23 | decisión de Jairo, 2-nov-2026 | `egm.esquema`, `egm.textos` | T-001-32, T-001-34 |  | diseñado |
| FR-001-24 | decisión de Jairo, 3-nov-2026 | `egm.lectura` | T-001-33 |  | diseñado |
| FR-001-25 | decisión de Jairo, 2-nov-2026 | `egm.verificacion`, `app.presentacion` (ADR-002) | T-001-44, T-001-46, T-001-66 |  | diseñado |
| FR-001-26 | decisión de Jairo, 2-nov-2026 | `egm.verificacion` (ADR-002) | T-001-43 |  | diseñado |
| FR-001-27 | decisión de Jairo, 2-nov-2026 | `egm.verificacion` (ADR-002) | T-001-44 |  | diseñado |
| FR-001-28 | decisión de Jairo, 2-nov-2026 | `app.sesiones`, `app.cliente`, `app.servidor` | T-001-82, T-001-83, T-001-84, T-001-85 |  | diseñado |
| FR-001-29 | decisión de Jairo, 3-nov-2026; decisión de Jairo, 21-nov-2026 | `app.carga`, `app.sesiones`, `egm.procesamiento`, `egm.archivo`, `egm.textos` (ADR-004) | T-001-15, T-001-17, T-001-51, T-001-64, T-001-65, T-001-70, T-003-63 |  | diseñado |
| FR-002-01 | lámina 5; doc. general §2.2; decisión de Jairo, 3-nov-2026 | `egm.conteo`, `egm.esquema`, `app.presentacion` | T-002-13, T-002-16 |  | diseñado |
| FR-002-02 | doc. general §3; doc. técnico §4.1 | `app.presentacion`, `app.plantillas` | T-002-13, T-002-14 |  | diseñado |
| FR-002-03 | lámina 5; doc. general §2.2 | `egm.conteo`, `app.presentacion`, `app.plantillas` | T-002-07, T-002-13, T-002-14 |  | diseñado |
| FR-002-04 | doc. general §7; lámina 5 | `egm.textos`, `app.presentacion` | T-002-12, T-002-13, T-002-29 |  | diseñado |
| FR-002-05 | doc. general §4.2; doc. técnico §4.1 | `egm.conteo`, `app.presentacion`, `app.plantillas` | T-002-29, T-002-30, T-002-31 |  | diseñado |
| FR-002-06 | doc. técnico §4.1 | `app.presentacion` | T-002-29 |  | diseñado |
| FR-002-07 | doc. técnico §4.1 RF4 | `egm.lectura`, `app.presentacion` | T-002-29, T-002-31 |  | diseñado |
| FR-002-08 | doc. general §3; decisión de Jairo, 2-nov-2026 | `egm.definiciones`, `app.configuracion`, `app.presentacion` (ADR-004) | T-002-34, T-002-35, T-002-36, T-002-37 |  | diseñado |
| FR-002-09 | doc. general §4.3; decisión de Jairo, 2-nov-2026 | `egm.filtros`, `app.presentacion` | T-002-20, T-002-22 |  | diseñado |
| FR-002-10 | decisión de Jairo, 1-nov-2026 | `egm.filtros` | T-002-20 |  | diseñado |
| FR-002-11 | doc. técnico §4.1 RF2; decisión de Jairo, 2-nov-2026 | `egm.filtros` | T-002-06, T-002-20 |  | diseñado |
| FR-002-12 | decisión de Jairo, 1-nov-2026; decisión de Jairo, 3-nov-2026 (provisional); decisión de Jairo, 21-nov-2026 | `egm.filtros`, `app.presentacion` | T-002-20, T-002-22, T-002-24, T-003-56 |  | diseñado |
| FR-002-13 | decisión de Jairo, 1-nov-2026 | `egm.filtros`, `egm.conteo`, `app.presentacion` | T-002-07, T-002-20, T-002-21, T-002-22, T-002-24 |  | diseñado |
| FR-002-14 | decisión de Jairo, 1-nov-2026 | `egm.textos`, `app.presentacion` | T-002-12, T-002-21, T-002-22, T-002-29, T-002-49 |  | diseñado |
| FR-002-15 | decisión de Jairo, 1-nov-2026 | `app.sesiones` (ADR-003) | T-002-08, T-002-16, T-002-23, T-002-30 |  | diseñado |
| FR-002-16 | doc. general §3; doc. técnico §4.1 | `app.exportacion`, `app.cliente` (M19) (ADR-003) | T-002-39, T-002-40, T-002-41, T-002-42 |  | diseñado |
| FR-002-17 | doc. general §4.1 | `egm.textos`, `app.presentacion` | T-002-13 |  | diseñado |
| FR-002-18 | decisión de Jairo, 21-nov-2026 | `egm.filtros`, `app.servidor`, `app.sesiones` | T-002-23, T-003-63 |  | diseñado |
| FR-002-19 | decisión de Jairo, 2-nov-2026; decisión de Jairo, 21-nov-2026 | `egm.filtros`, `app.servidor`, `app.sesiones` (ADR-003) | T-002-06, T-002-08, T-002-20, T-002-21, T-002-23, T-002-24, T-003-63 |  | diseñado |
| FR-003-01 | doc. general §9 | `egm.conclusiones` | T-003-13, T-003-14, T-003-15, T-003-16 |  | diseñado |
| FR-003-02 | decisión de Jairo, 1-nov-2026 | `egm.conclusiones` | T-003-13 |  | diseñado |
| FR-003-03 | doc. general §9 | `app.presentacion`, `app.plantillas` | T-003-16, T-003-48, T-003-49, T-003-61, T-003-62 |  | diseñado |
| FR-003-04 | doc. general §5, §7 | `egm.conclusiones`, `app.presentacion` (ADR-001) | T-003-08, T-003-15, T-003-22, T-003-26, T-003-27, T-003-48, T-003-49, T-003-93 |  | diseñado |
| FR-003-05 | doc. general §5.1 | `egm.conclusiones`, `egm.textos` | T-003-22, T-003-25 |  | diseñado |
| FR-003-06 | doc. general §5.2 | `egm.conclusiones`, `egm.conteo` | T-002-07, T-003-23 |  | diseñado |
| FR-003-07 | doc. general §5.3; doc. técnico §6.6; decisión de Jairo, 22-nov-2026 | `egm.conclusiones`, `egm.lectura` | T-003-24 |  | diseñado |
| FR-003-08 | doc. general §5.4 | `egm.conclusiones`, `egm.conteo` | T-003-43, T-003-44 |  | diseñado |
| FR-003-09 | doc. general §5.5; doc. técnico §6.9 | `egm.conclusiones` | T-003-45 |  | diseñado |
| FR-003-10 | doc. general §5.6; doc. técnico §6.11 | `egm.conclusiones` | T-003-46 |  | diseñado |
| FR-003-11 | doc. general §7 | `egm.conclusiones`, `egm.textos` | T-003-22, T-003-23, T-003-24, T-003-25, T-003-44, T-003-47 |  | diseñado |
| FR-003-12 | doc. general §5 | `egm.textos` | T-003-25, T-003-47, T-003-92 |  | diseñado |
| FR-003-13 | decisión de Jairo, 1-nov-2026 | `egm.filtros`, `app.sesiones`, `app.presentacion` | T-003-54, T-003-56, T-003-57, T-003-61, T-003-63 |  | diseñado |
| FR-003-14 | decisión de Jairo, 1-nov-2026; doc. general §9; decisión de Jairo, 21-nov-2026 | `egm.filtros`, `egm.conclusiones`, `app.presentacion` | T-002-07, T-003-53, T-003-54, T-003-56 |  | diseñado |
| FR-003-15 | decisión de Jairo, 1-nov-2026 | `egm.textos`, `app.presentacion` | T-003-55, T-003-57 |  | diseñado |
| FR-003-16 | decisión de Jairo, 1-nov-2026 | `egm.conclusiones`, `egm.textos` | T-003-54, T-003-55 |  | diseñado |
| FR-003-17 | doc. general §7; decisión de Jairo, 1-nov-2026 | `egm.porcentajes`, `egm.conclusiones` | T-003-06, T-003-36 |  | diseñado |
| FR-003-18 | doc. general §7 | `egm.conclusiones`, `egm.textos` (ADR-001) | T-003-32, T-003-33 |  | diseñado |
| FR-003-19 | doc. general §2.3 | `egm.textos`, `app.presentacion` | T-003-32, T-003-34, T-003-35 |  | diseñado |
| FR-003-20 | doc. general §7 | `egm.verificacion`, `egm.textos`, `app.presentacion` (ADR-002) | T-003-34, T-003-35 |  | diseñado |
| FR-003-21 | Matriz Instrucciones B20; decisión de Jairo, 2-nov-2026; decisión de Jairo, 21-nov-2026 | `egm.conclusiones`, `egm.conteo` | T-003-13, T-003-14 |  | diseñado |
| FR-003-22 | decisión de Jairo, 2-nov-2026 | `egm.conclusiones`, `egm.esquema` | T-003-23 |  | diseñado |

## Cobertura de la fase de specs

Escenario o criterio que verifica cada requisito.

| Requisito | Verificado por |
|---|---|
| NFR-000-01 | SC-000-01, US-001-4.6 |
| NFR-000-02 | SC-000-02 |
| NFR-000-03 | SC-000-03 |
| NFR-000-04 | SC-000-04, SC-002-04 |
| NFR-000-05 | SC-000-05 |
| NFR-000-06 | SC-000-06, US-001-3.11, US-001-3.12 |
| NFR-000-07 | SC-000-07 |
| NFR-000-08 | SC-000-08 |
| NFR-000-09 | SC-000-09 |
| NFR-000-10 | SC-000-10 |
| NFR-000-11 | SC-000-11 |
| NFR-000-12 | SC-000-12 |
| NFR-000-13 | SC-000-13 |
| NFR-000-14 | SC-000-14 |
| NFR-000-15 | SC-000-15 |
| NFR-000-16 | SC-000-16 |
| NFR-000-17 | SC-000-17, US-001-5.1, US-001-5.2, US-001-5.3, US-001-5.4, US-001-5.5, US-001-5.6, US-001-4.7 |
| NFR-000-18 | SC-000-18 |
| NFR-000-19 | SC-000-19, US-001-4.3, US-001-4.4, US-001-4.13 |
| FR-001-01 | US-001-1.8, US-001-3.5, SC-001-05 |
| FR-001-02 | US-001-2.4, US-001-2.7, SC-001-02 |
| FR-001-03 | US-001-1.4, US-001-2.5 |
| FR-001-04 | US-001-2.6 |
| FR-001-05 | US-001-1.3, US-001-2.12 |
| FR-001-06 | US-001-1.5 |
| FR-001-07 | US-001-1.1, US-001-1.10, SC-001-01 |
| FR-001-08 | US-001-1.2, US-001-2.2, SC-001-01, SC-001-03 |
| FR-001-09 | US-001-1.2, SC-001-01, SC-001-03 |
| FR-001-10 | US-001-1.6, US-001-2.14 |
| FR-001-11 | US-001-1.7 |
| FR-001-12 | US-001-2.1, SC-001-02, SC-001-04 |
| FR-001-13 | US-001-1.9, US-001-2.3, US-001-2.15, US-001-2.16 |
| FR-001-14 | US-001-3.1, US-001-3.2 |
| FR-001-15 | US-001-3.5, US-001-3.9 |
| FR-001-16 | US-001-3.3, US-001-3.4, US-001-3.6 |
| FR-001-17 | US-001-3.3, US-001-3.13 |
| FR-001-18 | US-001-3.2, US-001-3.8, US-001-3.17 |
| FR-001-19 | US-001-1.7 |
| FR-001-20 | US-001-4.1, US-001-4.2, US-001-4.5 |
| FR-001-21 | US-001-2.8 |
| FR-001-22 | US-001-2.11, US-001-2.12, US-001-2.15, SC-001-02 |
| FR-001-23 | US-001-2.9, US-001-2.10 |
| FR-001-24 | US-001-2.13 |
| FR-001-25 | US-001-3.3, US-001-3.7 |
| FR-001-26 | US-001-3.9, US-001-3.10, US-001-3.15, US-001-3.16 |
| FR-001-27 | US-001-3.11, US-001-3.12, US-001-3.13, US-001-3.14 |
| FR-001-28 | US-001-5.1 |
| FR-001-29 | US-001-4.7, US-001-4.8, US-001-4.9, US-001-4.10, US-001-4.11, US-001-4.12, US-001-4.13 |
| FR-002-01 | US-002-1.1, US-002-1.4, US-002-1.7 |
| FR-002-02 | US-002-1.2, SC-002-01 |
| FR-002-03 | US-002-1.3 |
| FR-002-04 | US-002-2.3 |
| FR-002-05 | US-002-2.1, SC-002-02 |
| FR-002-06 | US-002-2.2 |
| FR-002-07 | US-002-2.4 |
| FR-002-08 | US-002-3.1, US-002-3.2, US-002-3.3 |
| FR-002-09 | US-002-4.1, US-002-4.9 |
| FR-002-10 | US-002-4.4 |
| FR-002-11 | US-002-4.3, US-002-4.8 |
| FR-002-12 | US-002-4.5, US-002-4.11, US-002-4.12, US-002-4.14 |
| FR-002-13 | US-002-4.1, SC-002-03 |
| FR-002-14 | US-002-4.2 |
| FR-002-15 | US-002-4.7, US-003-3.4, US-003-5.1, US-003-5.2 |
| FR-002-16 | US-002-5.1, US-002-5.2, SC-002-05 |
| FR-002-17 | US-002-1.5, US-002-1.6 |
| FR-002-18 | US-002-4.6 |
| FR-002-19 | US-002-4.6, US-002-4.10, US-002-4.13, US-003-5.4, US-003-5.5 |
| FR-003-01 | US-003-1.1, SC-003-02 |
| FR-003-02 | US-003-1.3 |
| FR-003-03 | US-003-1.4, US-003-5.3 |
| FR-003-04 | US-003-1.2, US-003-2.8, SC-003-01, SC-003-05 |
| FR-003-05 | US-003-2.1 |
| FR-003-06 | US-003-2.2 |
| FR-003-07 | US-003-2.4 |
| FR-003-08 | US-003-2.5, US-003-2.9 |
| FR-003-09 | US-003-2.6 |
| FR-003-10 | US-003-2.7 |
| FR-003-11 | US-003-2.3 |
| FR-003-12 | SC-003-04, SC-003-06 |
| FR-003-13 | US-003-3.1 |
| FR-003-14 | US-002-4.14, US-003-3.1, US-003-3.5, SC-003-03 |
| FR-003-15 | US-003-3.3 |
| FR-003-16 | US-003-3.2 |
| FR-003-17 | US-003-4.1 |
| FR-003-18 | US-003-4.2 |
| FR-003-19 | US-003-4.3 |
| FR-003-20 | US-003-4.4, US-003-4.5 |
| FR-003-21 | US-003-1.5 |
| FR-003-22 | US-003-2.10 |
