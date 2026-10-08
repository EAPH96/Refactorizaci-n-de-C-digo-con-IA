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
| 1  |              |                  |               |          |
| 2  |              |                  |               |          |
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
