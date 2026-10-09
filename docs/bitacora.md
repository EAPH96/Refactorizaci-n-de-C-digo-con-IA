# Bitácora de refactorización

**Nombre:** Emiliano Antonio Pineda Hernández
**Matrícula:** A01332517
**Fecha:** 2026-10-07

Registra aquí **cada refactorización** que realices con Claude Code. Copia el
prompt tal cual lo escribiste (o un resumen fiel si fue una conversación larga),
describe el cambio que se aplicó al código y justifica por qué mejora la calidad.
Después de cada cambio ejecuta `pytest` y anota el resultado.

> **Cómo se valida cada refactorización.** Después de cada cambio se ejecutan
> tres verificaciones y no se avanza a la siguiente refactorización hasta que
> las tres estén en verde:
>
> 1. `pytest -v` — suite oficial de caja negra (20 pruebas, no se modifica).
> 2. Suite de **caracterización** en `tests_caracterizacion/` (fuera de `tests/`,
>    que no se modifica): 12 pruebas *golden master* creadas antes de
>    refactorizar, que comparan ticket, reportes, menú, archivo JSON y mensajes
>    de error contra el comportamiento original, más 8 casos límite
>    descubiertos durante las fases (20 en total desde R10).
> 3. `ruff check src` — el conteo de errores debe bajar o mantenerse.
>
> Formato de la columna *Tests OK*: `✅ 20/20 · caract. N/N · ruff N`.
> Si una prueba falla, se registra en **Incidencias** (qué falló, causa,
> corrección) y se corrige el código antes de continuar.

## Línea base (antes de refactorizar)

| Verificación | Resultado |
|---|---|
| `pytest` | ✅ 20/20 |
| Caracterización | ✅ 12/12 (8 escenarios + 4 invariantes) |
| `ruff check src` | ❌ 20 errores (UP009 ×4, SIM102 ×3, SIM115 ×3, C901 ×2, N802 ×2, N816, SIM103, SIM108, I001, F401, UP015) |

> Prueba de la red de seguridad: se introdujeron a propósito dos cambios sutiles
> (formato `$23.20` en lugar de `$23.2` y umbral VIP `>= 200` en lugar de `> 200`).
> La suite oficial siguió en 20/20 en ambos casos; la de caracterización los
> detectó (3 y 1 fallos). Ambos cambios se revirtieron.

## Refactorizaciones

> **Prompt usado:** cada fila resume el prompt de esa fase del plan de
> refactorización. Todos siguen el mismo ciclo: analizar sin editar → esperar
> aprobación → refactorizar → verificar (pytest, caracterización y ruff) →
> documentar.

| #  | Prompt usado | Cambio realizado | Justificación | Tests OK |
|----|--------------|------------------|---------------|----------|
| 1  | Eliminar código sin referencias, sin tocar nada más | Se borraron `calcular_descuento_viejo()`, `exportar_txt` (comentado), `MODO_DEBUG`, `reporteViejoCSV()`, `import os` y las cabeceras `coding` | Código que no se usaba y confundía; Git guarda la historia | ✅ 20/20 · caract. 12/12 · ruff 13 |
| 2  | Reemplazar números mágicos por constantes, con los mismos comparadores | 13 constantes: umbrales, tasas, IVA, regla VIP, formato de fecha, ticket, stock mínimo y top de ventas | Una sola fuente para cada regla de negocio; el código dice qué compara | ✅ 20/20 · caract. 12/12 · ruff 13 |
| 3  | Extraer el cálculo duplicado entre venta y cotización, respetando el contrato de precios | `calcular_descuento()` y `calcular_impuesto()` compartidas; los 4 `if` del VIP en una condición | Sin duplicación; `registrar_venta` baja de complejidad 12 a 6 | ✅ 20/20 · caract. 12/12 · ruff 8 |
| 4  | Cláusulas de guarda con el mismo orden y mensajes de validación | La pirámide de `if/else` pasa a `_validar_venta()` con salidas tempranas | Se lee de arriba abajo; se usó `not x > 0` (no `x <= 0`) para no cambiar el caso `NaN` | ✅ 20/20 · caract. 12/12 · ruff 8 |
| 5  | Separar el ticket y el registro de `registrar_venta` | `_generar_ticket()`; venta y producto como diccionarios literales | Separa presentación de lógica; la función pasa de 46 a 31 líneas | ✅ 20/20 · caract. 12/12 · ruff 8 |
| 6  | Usar `with` y simplificar `almacen.py` sin cambiar la carga | `with open`, sin modo `"r"`, `hay_archivo` directo, ventas con `extend` | El archivo siempre se cierra; se conservaron el bucle y `except Exception` por equivalencia | ✅ 20/20 · caract. 12/12 · ruff 4 |
| 7  | Renombrar a PEP 8 con nombres descriptivos | `contador_ventas`, `hay_archivo`, `formatear_dinero` y ~40 variables locales | El código se explica solo; estilo snake_case consistente | ✅ 20/20 · caract. 12/12 · ruff 2 (intento 2) |
| 8  | Menú con una función por opción y tabla de despacho | 6 funciones de opción + diccionario `OPCIONES`; imports ordenados | `menu()` pasa de 66 a 17 líneas y de complejidad 17 a 4 | ✅ 20/20 · caract. 12/12 · ruff 0 |
| 9  | Reportes y búsqueda con idiomas de Python, sin cambiar resultados | `sorted` en lugar de burbuja, comprensiones, `_es_stock_bajo()`, `join` y reuso de `total_vendido()` | Biblioteca estándar y sin duplicación; se descartaron 4 simplificaciones que cambiaban resultados | ✅ 20/20 · caract. 12/12 · ruff 0 |
| 10 | Type hints y docstrings consistentes, sin tocar la lógica | Anotaciones con sintaxis 3.10 en las 31 funciones, alias `Producto`/`Venta`, docstrings en las 6 funciones que no tenían y docstring de `gestor` sin "hay de todo un poco" | Contratos visibles en el código; el AST sin anotaciones es idéntico al de R9 | ✅ 20/20 · caract. 20/20 · ruff 0 |

> Agrega más filas si realizas más de 5 refactorizaciones.

## Incidencias

Pruebas que fallaron durante alguna refactorización, su causa y cómo se corrigió.

| Refactorización | Intento | Pruebas que fallaron | Pruebas que pasaron | Causa | Corrección |
|---|---|---|---|---|---|
| R7 | 1 | Ninguna prueba; ruff marcó un `E501` (línea de 89 caracteres) | 20/20 · 12/12 | Un nombre más largo alargó una línea de `mas_vendidos` | Se reescribió con `+=`; intento 2: ruff 2 |

## Correcciones a la IA

Instrucciones que se enviaron **después** del prompt principal de una
refactorización para modificar lo que propuso o hizo la IA.

| Refactorización | Corrección | Instrucción (resumen) | Qué se cambió |
|---|---|---|---|
| — | — | Sin correcciones por ahora | — |

## Pruebas adicionales para casos límite

Además de la suite *golden master*, `tests_caracterizacion/test_casos_limite.py`
tiene 8 pruebas de comportamientos descubiertos durante las fases, que ninguna suite cubría:

| Fase | Caso | Comportamiento que se conserva |
|---|---|---|
| R4 | Cantidad o stock `NaN` | Se rechaza (`cantidad invalida` / `stock insuficiente`) |
| R6 | Archivo con bytes no UTF-8 | `False` + `archivo corrupto` |
| R6 | `"inventario": ["ab"]` | `TypeError` en lugar de cargar `{"a": "b"}` |
| R9 | Venta con cantidad `True` | `mas_vendidos` regresa `True`, no `1` |
| R9 | `buscarProducto(None)` | `[]` con inventario vacío; `AttributeError` con productos |
| R9 | Código no textual en reporte | `TypeError`, como el original |

Se verificaron con mutaciones: al aplicar la versión "obvia" (`cantidad <= 0` o
`except json.JSONDecodeError`), la prueba correspondiente falla.

## Variaciones de prompts y lecciones del proceso

- **Analizar antes de editar.** Cada prompt de fase obligaba a presentar un
  análisis y esperar aprobación. Así aparecieron casi todas las trampas
  (`NaN`, `dict.update`, f-strings, `sum()`) **antes** de escribir código.
- **Contrato explícito frente a "mejorar el código".** Los prompts con la
  sección *Invariantes* y *No hagas* evitaron cambios plausibles que rompían
  el comportamiento (`$23.20`, `base * 1.16`, excepciones en lugar de `None`).
- **La suite oficial no basta.** Dos mutaciones sutiles pasaron 20/20; por
  eso se agregó la caracterización desde la línea base.
- **Comprobaciones de equivalencia en los cambios de riesgo.** R3, R5 y R9
  compararon la versión anterior contra la nueva con miles de casos
  aleatorios; R4 demostró que la forma "obvia" cambiaba 14 casos sin que
  ninguna suite lo notara.
- **Renombrar por tokens, no con buscar y reemplazar** (R7): un reemplazo de
  `n` → `nombre` habría roto los `"\n"` de los reportes.
- **Versión completa contra versión completa** (R7): comparar un
  `almacen.py` viejo con un `gestor.py` nuevo dio un falso error; al
  renombrar algo compartido entre módulos hay que comparar todo `src/`.
- **Iteración de `CLAUDE.md`:** tuvo 6 versiones durante el reto (protocolo
  ante fallos, caracterización obligatoria, registro de correcciones,
  `contador_ventas`, ubicación de la suite). El historial está en su §10.

## Logs de la ejecución final

```text
$ pytest -v
tests/test_almacen.py::test_guardar_y_cargar_conserva_los_datos PASSED
...
tests/test_reportes.py::test_reporte_inventario_marca_stock_bajo PASSED
============================== 20 passed ==============================

$ pytest tests_caracterizacion -v
test_caracterizacion.py::test_escenario_identico_a_linea_base[ventas] PASSED
...
test_casos_limite.py::TestR9Reportes::test_reporte_con_codigo_no_textual_falla_igual_que_antes PASSED
============================== 20 passed ==============================

$ ruff check src
All checks passed!
```

## Reflexión final (10-15 líneas)

Responde: ¿Qué tan útil fue Claude Code para detectar y corregir los problemas?
¿Qué propuso la IA que tú no habías notado? ¿En qué casos tuviste que corregir
o rechazar sus sugerencias? ¿Qué aprendiste sobre refactorizar con apoyo de IA?

> Reflexión completa: [`docs/reflexion.md`](reflexion.md). Aquí va el resumen
> de 10-15 líneas que pide la plantilla.

Me pareció muy útil y muy rápido poder realizar las identificaciones de áreas de oportunidad del código, todo bien documentado para detectar y corregir los problemas de forma automática. Me gustó mucho la actividad porque justo aprendí el cómo es que se mejoraba un código desde múltiples aspectos, me ayudó a conocer y estudiar nuevas técnicas de refactorización que podré aplicar dentro de mi día a día. Tengo que seguir practicando para mejorar mi uso de la IA en mi día a día.
