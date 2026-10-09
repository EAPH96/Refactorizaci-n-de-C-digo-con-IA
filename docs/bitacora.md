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
> 2. Suite de **caracterización** (12 pruebas, *golden master*) creada antes de
>    refactorizar: compara ticket, reportes, menú de consola, archivo JSON,
>    mensajes de error y casos límite contra una captura del comportamiento
>    original. Cubre zonas que la suite oficial no prueba.
> 3. `ruff check src` — el conteo de errores debe bajar o mantenerse.
>
> Formato de la columna *Tests OK*: `✅ 20/20 · caract. 12/12 · ruff N`.
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

## Reflexión final (10-15 líneas)

Responde: ¿Qué tan útil fue Claude Code para detectar y corregir los problemas?
¿Qué propuso la IA que tú no habías notado? ¿En qué casos tuviste que corregir
o rechazar sus sugerencias? ¿Qué aprendiste sobre refactorizar con apoyo de IA?

> Reflexión completa: [`docs/reflexion.md`](reflexion.md). Aquí va el resumen
> de 10-15 líneas que pide la plantilla.

Me pareció muy útil y muy rápido poder realizar las identificaciones de áreas de oportunidad del código, todo bien documentado para detectar y corregir los problemas de forma automática. Me gustó mucho la actividad porque justo aprendí el cómo es que se mejoraba un código desde múltiples aspectos, me ayudó a conocer y estudiar nuevas técnicas de refactorización que podré aplicar dentro de mi día a día. Tengo que seguir practicando para mejorar mi uso de la IA en mi día a día.
