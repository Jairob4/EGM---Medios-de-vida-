# Matriz de trazabilidad

Fuente → requisito → componente → tarea → prueba. Cada fase llena su columna; ninguna borra lo de la anterior.

| Requisito | Fuente | Componente (ADR/arquitectura) | Tarea (plan) | Prueba | Estado |
|---|---|---|---|---|---|
| NFR-000-01 | doc. técnico §4.2 RNF1; decisión de Jairo, 2-nov-2026 | `egm.libro`, `app.carga` (ADR-001, ADR-004) |  |  | especificado |
| NFR-000-02 | doc. general §4.2; doc. técnico §4.2 RNF4 | `egm.modelo`, `egm.conteo`, `egm.conclusiones`, `app.presentacion` (ADR-001) |  |  | especificado |
| NFR-000-03 | estado §5 | `egm.textos`, `app.plantillas` |  |  | especificado |
| NFR-000-04 | prompt de la fase 1, T3 | `app.plantillas`, `app.cliente` (ADR-003) |  |  | especificado |
| NFR-000-05 | prompt de la fase 1, T3 | `app.plantillas` (ADR-003) |  |  | especificado |
| NFR-000-06 | doc. general §9; decisión de Jairo, 1-nov-2026; decisión de Jairo, 2-nov-2026 | `egm.esquema`, `egm.lectura`, `egm.conteo`, `tests.constructor`, `app.presentacion` (M17), `app.plantillas` (M18) (ADR-001) |  |  | especificado |
| NFR-000-07 | doc. general §7; decisión de Jairo, 1-nov-2026 | `egm.porcentajes`, `app.configuracion` |  |  | especificado |
| NFR-000-08 | doc. general §7; lámina 5 | `egm.textos`, `app.presentacion` |  |  | especificado |
| NFR-000-09 | doc. técnico §4.2 RNF2 | `egm.procesamiento`, `egm.modelo`, `app.presentacion`, `app.exportacion` (ADR-001) |  |  | especificado |
| NFR-000-10 | doc. técnico §4.2 RNF5 | `app.presentacion`, `app.plantillas` |  |  | especificado |
| NFR-000-11 | decisión de Jairo, 31-oct-2026; decisión de Jairo, 2-nov-2026 | `app.colofon`, `app.configuracion`, `app.plantillas` (ADR-005: bloques institucionales apagados por defecto) |  |  | especificado |
| NFR-000-12 | decisión de Jairo, 31-oct-2026; decisión de Jairo, 2-nov-2026; decisión de Jairo, 3-nov-2026 | `app.colofon`, `app.presentacion`, `egm.procesamiento` (ADR-005) |  |  | especificado |
| NFR-000-13 | decisión de Jairo, 31-oct-2026 | `app.plantillas` (ADR-003) |  |  | especificado |
| NFR-000-14 | decisión de Jairo, 31-oct-2026 | núcleo `egm.*` sin dependencias web; `egm.procesamiento`; puntos de extensión PE-1 a PE-7 (arquitectura §7) |  |  | especificado |
| NFR-000-15 | doc. general §4.2; decisión de Jairo, 31-oct-2026 | `app.servidor` (ADR-003, ADR-004) |  |  | especificado |
| NFR-000-16 | doc. general §3 | `app.colofon`, `app.plantillas` (ADR-005) |  |  | especificado |
| NFR-000-17 | decisión de Jairo, 2-nov-2026; decisión de Jairo, 3-nov-2026; decisión de Jairo, 21-nov-2026 | `app.sesiones`, `app.carga`, `app.cliente`, `app.servidor` (ADR-003, ADR-004) |  |  | especificado |
| NFR-000-18 | decisión de Jairo, 2-nov-2026 | `app.sesiones` (ADR-003) |  |  | especificado |
| NFR-000-19 | decisión de Jairo, 2-nov-2026; decisión de Jairo, 3-nov-2026; decisión de Jairo, 21-nov-2026 | `egm.archivo`, `app.carga` (ADR-003, ADR-004) |  |  | especificado |
| FR-001-01 | doc. técnico §5.1 | `egm.esquema`, `egm.libro` |  |  | especificado |
| FR-001-02 | doc. técnico §5.1, §5.3 | `egm.esquema`, `egm.textos` |  |  | especificado |
| FR-001-03 | decisión de Jairo, 1-nov-2026 | `egm.esquema` |  |  | especificado |
| FR-001-04 | decisión de Jairo, 1-nov-2026 | `egm.esquema` |  |  | especificado |
| FR-001-05 | doc. técnico §12.2 | `egm.libro`, `egm.esquema` (ADR-001) |  |  | especificado |
| FR-001-06 | doc. técnico §9.2 | `egm.lectura` (ADR-001) |  |  | especificado |
| FR-001-07 | Matriz Instrucciones B20; lámina 6; decisión de Jairo, 3-nov-2026 | `egm.conteo` (ADR-001) |  |  | especificado |
| FR-001-08 | doc. general §7 | `egm.conteo` (ADR-001) |  |  | especificado |
| FR-001-09 | doc. técnico §2.4 | `egm.conteo` (ADR-001) |  |  | especificado |
| FR-001-10 | Matriz Instrucciones B14; doc. técnico §6.6; decisión de Jairo, 2-nov-2026 | `egm.lectura`, `egm.textos` |  |  | especificado |
| FR-001-11 | doc. general §4.2 | `egm.modelo`, `egm.conteo` (ADR-001) |  |  | especificado |
| FR-001-12 | doc. técnico §9.2 | `egm.lectura`, `egm.esquema`, `egm.verificacion`, `egm.textos` |  |  | especificado |
| FR-001-13 | doc. técnico §9.2; decisión de Jairo, 2-nov-2026 | `egm.lectura`, `egm.conteo` |  |  | especificado |
| FR-001-14 | doc. general §4.1; doc. técnico §9.1 | `egm.verificacion`, `egm.conteo`, `tests.constructor` (ADR-002) |  |  | especificado |
| FR-001-15 | decisión de Jairo, 1-nov-2026 | `egm.verificacion` (ADR-002) |  |  | especificado |
| FR-001-16 | decisión de Jairo, 1-nov-2026 | `egm.verificacion` (ADR-002) |  |  | especificado |
| FR-001-17 | doc. técnico §9.1 | `egm.verificacion`, `egm.libro` (ADR-002) |  |  | especificado |
| FR-001-18 | doc. general §4.1; doc. técnico §3.2 | `egm.verificacion`, `egm.textos`, `app.presentacion` (ADR-002) |  |  | especificado |
| FR-001-19 | doc. técnico §4.2 RNF2 | `egm.procesamiento`, `app.presentacion` |  |  | especificado |
| FR-001-20 | decisión de Jairo, 2-nov-2026; decisión de Jairo, 3-nov-2026 | `app.carga`, `app.cliente`, `app.sesiones`, `egm.archivo` (ADR-004) |  |  | especificado |
| FR-001-21 | decisión de Jairo, 2-nov-2026 | `egm.esquema` |  |  | especificado |
| FR-001-22 | decisión de Jairo, 2-nov-2026 | `egm.esquema` |  |  | especificado |
| FR-001-23 | decisión de Jairo, 2-nov-2026 | `egm.esquema`, `egm.textos` |  |  | especificado |
| FR-001-24 | decisión de Jairo, 3-nov-2026 | `egm.lectura` |  |  | especificado |
| FR-001-25 | decisión de Jairo, 2-nov-2026 | `egm.verificacion`, `app.presentacion` (ADR-002) |  |  | especificado |
| FR-001-26 | decisión de Jairo, 2-nov-2026 | `egm.verificacion` (ADR-002) |  |  | especificado |
| FR-001-27 | decisión de Jairo, 2-nov-2026 | `egm.verificacion` (ADR-002) |  |  | especificado |
| FR-001-28 | decisión de Jairo, 2-nov-2026 | `app.sesiones`, `app.cliente`, `app.servidor` |  |  | especificado |
| FR-001-29 | decisión de Jairo, 3-nov-2026; decisión de Jairo, 21-nov-2026 | `app.carga`, `app.sesiones`, `egm.procesamiento`, `egm.archivo`, `egm.textos` (ADR-004) |  |  | especificado |
| FR-002-01 | lámina 5; doc. general §2.2; decisión de Jairo, 3-nov-2026 | `egm.conteo`, `egm.esquema`, `app.presentacion` |  |  | especificado |
| FR-002-02 | doc. general §3; doc. técnico §4.1 | `app.presentacion`, `app.plantillas` |  |  | especificado |
| FR-002-03 | lámina 5; doc. general §2.2 | `egm.conteo`, `app.presentacion`, `app.plantillas` |  |  | especificado |
| FR-002-04 | doc. general §7; lámina 5 | `egm.textos`, `app.presentacion` |  |  | especificado |
| FR-002-05 | doc. general §4.2; doc. técnico §4.1 | `egm.conteo`, `app.presentacion`, `app.plantillas` |  |  | especificado |
| FR-002-06 | doc. técnico §4.1 | `app.presentacion` |  |  | especificado |
| FR-002-07 | doc. técnico §4.1 RF4 | `egm.lectura`, `app.presentacion` |  |  | especificado |
| FR-002-08 | doc. general §3; decisión de Jairo, 2-nov-2026 | `egm.definiciones`, `app.configuracion`, `app.presentacion` (ADR-004) |  |  | especificado |
| FR-002-09 | doc. general §4.3; decisión de Jairo, 2-nov-2026 | `egm.filtros`, `app.presentacion` |  |  | especificado |
| FR-002-10 | decisión de Jairo, 1-nov-2026 | `egm.filtros` |  |  | especificado |
| FR-002-11 | doc. técnico §4.1 RF2; decisión de Jairo, 2-nov-2026 | `egm.filtros` |  |  | especificado |
| FR-002-12 | decisión de Jairo, 1-nov-2026; decisión de Jairo, 3-nov-2026 (provisional); decisión de Jairo, 21-nov-2026 | `egm.filtros`, `app.presentacion` |  |  | especificado |
| FR-002-13 | decisión de Jairo, 1-nov-2026 | `egm.filtros`, `egm.conteo`, `app.presentacion` |  |  | especificado |
| FR-002-14 | decisión de Jairo, 1-nov-2026 | `egm.textos`, `app.presentacion` |  |  | especificado |
| FR-002-15 | decisión de Jairo, 1-nov-2026 | `app.sesiones` (ADR-003) |  |  | especificado |
| FR-002-16 | doc. general §3; doc. técnico §4.1 | `app.exportacion`, `app.cliente` (M19) (ADR-003) |  |  | especificado |
| FR-002-17 | doc. general §4.1 | `egm.textos`, `app.presentacion` |  |  | especificado |
| FR-002-18 | decisión de Jairo, 21-nov-2026 | `egm.filtros`, `app.servidor`, `app.sesiones` |  |  | especificado |
| FR-002-19 | decisión de Jairo, 2-nov-2026; decisión de Jairo, 21-nov-2026 | `egm.filtros`, `app.servidor`, `app.sesiones` (ADR-003) |  |  | especificado |
| FR-003-01 | doc. general §9 | `egm.conclusiones` |  |  | especificado |
| FR-003-02 | decisión de Jairo, 1-nov-2026 | `egm.conclusiones` |  |  | especificado |
| FR-003-03 | doc. general §9 | `app.presentacion`, `app.plantillas` |  |  | especificado |
| FR-003-04 | doc. general §5, §7 | `egm.conclusiones`, `app.presentacion` (ADR-001) |  |  | especificado |
| FR-003-05 | doc. general §5.1 | `egm.conclusiones`, `egm.textos` |  |  | especificado |
| FR-003-06 | doc. general §5.2 | `egm.conclusiones`, `egm.conteo` |  |  | especificado |
| FR-003-07 | doc. general §5.3; doc. técnico §6.6 | `egm.conclusiones`, `egm.lectura` |  |  | especificado |
| FR-003-08 | doc. general §5.4 | `egm.conclusiones`, `egm.conteo` |  |  | especificado |
| FR-003-09 | doc. general §5.5; doc. técnico §6.9 | `egm.conclusiones` |  |  | especificado |
| FR-003-10 | doc. general §5.6; doc. técnico §6.11 | `egm.conclusiones` |  |  | especificado |
| FR-003-11 | doc. general §7 | `egm.conclusiones`, `egm.textos` |  |  | especificado |
| FR-003-12 | doc. general §5 | `egm.textos` |  |  | especificado |
| FR-003-13 | decisión de Jairo, 1-nov-2026 | `egm.filtros`, `app.sesiones`, `app.presentacion` |  |  | especificado |
| FR-003-14 | decisión de Jairo, 1-nov-2026; doc. general §9; decisión de Jairo, 21-nov-2026 | `egm.filtros`, `egm.conclusiones`, `app.presentacion` |  |  | especificado |
| FR-003-15 | decisión de Jairo, 1-nov-2026 | `egm.textos`, `app.presentacion` |  |  | especificado |
| FR-003-16 | decisión de Jairo, 1-nov-2026 | `egm.conclusiones`, `egm.textos` |  |  | especificado |
| FR-003-17 | doc. general §7; decisión de Jairo, 1-nov-2026 | `egm.porcentajes`, `egm.conclusiones` |  |  | especificado |
| FR-003-18 | doc. general §7 | `egm.conclusiones`, `egm.textos` (ADR-001) |  |  | especificado |
| FR-003-19 | doc. general §2.3 | `egm.textos`, `app.presentacion` |  |  | especificado |
| FR-003-20 | doc. general §7 | `egm.verificacion`, `egm.textos`, `app.presentacion` (ADR-002) |  |  | especificado |
| FR-003-21 | Matriz Instrucciones B20; decisión de Jairo, 2-nov-2026; decisión de Jairo, 21-nov-2026 | `egm.conclusiones`, `egm.conteo` |  |  | especificado |
| FR-003-22 | decisión de Jairo, 2-nov-2026 | `egm.conclusiones`, `egm.esquema` |  |  | especificado |

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
