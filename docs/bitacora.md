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

| #  | Prompt usado | Cambio realizado | Justificación | Tests OK |
|----|--------------|------------------|---------------|----------|
| 1  | "Comencemos con la refactorización, empieza con R1; cuando acabes corre los tests y muéstralos todos, cuáles pasaron y cuáles no [...]" + aprobación del alcance tras el análisis ("apruebo el alcance") | **Eliminar código muerto.** Se borraron `calcular_descuento_viejo()` y el bloque comentado `exportar_txt` (gestor), `MODO_DEBUG` (gestor), `reporteViejoCSV()` y `import os` (reportes) y las cabeceras `# -*- coding: utf-8 -*-` de los 4 módulos. 35 líneas eliminadas, 0 agregadas. | Nada de eso se ejecutaba ni tenía referencias (verificado con búsqueda en `src/` y `tests/`); solo confundía y había que mantenerlo. Git conserva la historia, así que el "por si acaso" sobra. Quita 7 de los 20 errores del linter sin tocar lógica. | ✅ 20/20 · caract. 12/12 · ruff 13 |
| 2  | "¿Podrías realizar la segunda [refactorización]?" + aprobación del alcance tras el análisis ("Apruebo el alcance a R2") | **Constantes con nombre en lugar de números mágicos.** 11 constantes en `gestor.py` (`UMBRAL_DESCUENTO_ALTO/MEDIO`, `TASA_DESCUENTO_ALTO/MEDIO`, `PREFIJO_VIP`, `MONTO_MINIMO_VIP`, `TASA_DESCUENTO_VIP`, `TASA_IVA`, `FORMATO_FECHA`, `ENCABEZADO_TICKET`, `SEPARADOR_TICKET`) y 2 en `reportes.py` (`STOCK_MINIMO`, `TOP_MAS_VENDIDOS`); el `3` de la regla VIP pasa a `len(PREFIJO_VIP)`. Mismos comparadores y orden de operaciones. | Las reglas de negocio estaban duplicadas como literales (IVA y descuentos en venta y cotización; el stock mínimo dos veces): ahora tienen una sola fuente de verdad y el código dice qué compara. Prepara R3 (cálculo de descuentos compartido). | ✅ 20/20 · caract. 12/12 · ruff 13 |
| 3  |              |                  |               |          |
| 4  |              |                  |               |          |
| 5  |              |                  |               |          |

> Agrega más filas si realizas más de 5 refactorizaciones.

## Incidencias

Pruebas que fallaron durante alguna refactorización, su causa y cómo se corrigió.

| Refactorización | Intento | Pruebas que fallaron | Pruebas que pasaron | Causa | Corrección |
|---|---|---|---|---|---|
| — | — | Sin incidencias por ahora | — | — | — |

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

*(Escribe aquí tu reflexión)*
