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
| 3  | "Realizar la tercera refactorización" + aprobación del alcance tras el análisis ("Sí, apruebo el alcance") | **Extraer el cálculo de montos compartido.** Nuevas funciones `calcular_descuento(subtotal, cliente="")` (volumen con `if/elif` + extra VIP en una sola condición con `startswith`) y `calcular_impuesto(base)`. `registrar_venta` y `cotizar` las usan en lugar de su copia del cálculo; `cotizar` llama sin cliente, así que sigue sin VIP. | El descuento estaba duplicado en venta y cotización y la regla VIP eran 4 `if` anidados. Ahora la política de precios vive en un solo lugar; `registrar_venta` baja de complejidad 12 a 6. Además de las suites, se compararon 20 000 compras aleatorias contra la versión anterior: todas idénticas. | ✅ 20/20 · caract. 12/12 · ruff 8 |
| 4  | "Sigue con R4" + aprobación del alcance tras el análisis ("Apruebo el alcance para R4") | **Cláusulas de guarda en la validación de la venta.** La pirámide de 4 niveles de `if/else` de `registrar_venta` se extrajo a `_validar_venta(codigo, cantidad)`: cada condición inválida sale de inmediato con su mensaje, en el mismo orden (código vacío → producto no existe → cantidad inválida → stock insuficiente). `registrar_venta` empieza con `if not _validar_venta(...): return None`. | Cada regla queda junto a su mensaje y el camino feliz deja de estar anidado (complejidad 6 → 3). Se negó la condición original (`not cantidad > 0`) en vez de invertirla (`cantidad <= 0`) porque con `NaN` no son equivalentes: la forma "obvia" habría cambiado 14 casos sin que ninguna suite lo detectara. Equivalencia verificada en 119 combinaciones. | ✅ 20/20 · caract. 12/12 · ruff 8 |
| 5  | "Continúa con R5" + aprobación del alcance tras el análisis ("apruebo el alcance de R5") | **Dividir `registrar_venta` y extraer el ticket.** El ticket se extrajo a `_generar_ticket(venta, descuento)` (lista de líneas + `join` en lugar de 8 concatenaciones `t = t + ...`); el registro de la venta y el del producto (`agregarProducto`) pasaron a diccionarios literales con el mismo orden de claves; nuevo docstring en lugar de "Esta funcion hace de todo". | Separa la presentación (ticket) de la lógica de la venta: `registrar_venta` queda como coordinadora (46 → 31 líneas). No se extrajo una función para el registro porque necesitaría 9 parámetros (otro *code smell*). Equivalencia verificada con 20 000 ventas aleatorias y 1 386 casos extremos de formato. | ✅ 20/20 · caract. 12/12 · ruff 8 |
| 6  | "Continúa con R6" + aprobación del alcance tras el análisis ("Apruebo el alcance de R6") | **Persistencia con context managers.** `almacen.py`: `with open(...)` en guardar y cargar (sin `close` manual duplicado), sin el modo `"r"` redundante, `hayArchivo` regresa `os.path.exists(...)` directo, el diccionario a guardar es un literal y la copia de ventas usa `extend`. Se conservaron a propósito el bucle del inventario y `except Exception`. | `with` garantiza que el archivo se cierre aunque haya errores. Las simplificaciones descartadas (`dict.update`, acotar la excepción) cambiaban el resultado con archivos mal formados o con bytes no UTF-8. Equivalencia contra R5: JSON idéntico byte por byte y 13 tipos de archivo cargados igual. | ✅ 20/20 · caract. 12/12 · ruff 4 |
| 7  | "Haz el R7" + aprobación del alcance tras el análisis ("Sí, lo apruebo") | **Nombres PEP 8 y descriptivos.** `contadorVentas` → `contador_ventas`, `hayArchivo` → `hay_archivo`, `hacer_cosa` → `formatear_dinero` y ~40 variables locales crípticas (`aux`, `temp2`, `t`, `s`, `p`, `op`, `cli`, `cant`…) con nombres que dicen qué guardan, en los 4 módulos. En `menu()`, `p` dejó de significar "precio" en una opción y "producto" en otra. | Código que se explica solo y estilo snake_case consistente (solo `agregarProducto`/`buscarProducto` se conservan porque los usan los tests). Se renombró por tokens de Python para no tocar cadenas como `"\n"`. Incidencia en el intento 1: ruff marcó un E501 por un nombre más largo (ver Incidencias). | ✅ 20/20 · caract. 12/12 · ruff 2 (intento 2; en el intento 1, ruff 3) |
| 8  | "Continúa con R8" + aprobación del alcance tras el análisis ("Apruebo el alcance de R8") | **Menú con tabla de despacho.** `menu()` (66 líneas, complejidad 17) se dividió en una función por opción (`_agregar_producto`, `_registrar_venta`, `_cotizar`…) y un diccionario `OPCIONES` (clave → etiqueta y acción) que sirve tanto para mostrar el menú como para ejecutar la opción; imports en orden alfabético. | Antes cada número de opción estaba dos veces (en el `print` y en el `elif`); ahora hay una sola fuente y agregar una opción no toca `menu()`, que queda en 17 líneas con complejidad 4. **Con esto `ruff check src` llega a 0 errores.** Consola idéntica a R7 en 300 secuencias aleatorias de entradas. | ✅ 20/20 · caract. 12/12 · ruff 0 |
| 9  | "Haz el R9" + aprobación del alcance tras el análisis ("Sí, lo apruebo") | **Idiomas de Python en reportes y búsqueda.** El ordenamiento de burbuja de `mas_vendidos` (con su `TODO: algun dia usar sorted`) pasa a `sorted(..., reverse=True)`; `productos_stock_bajo` y `buscarProducto` usan comprensiones; `_es_stock_bajo()` elimina la condición duplicada en dos reportes; los reportes se arman como lista de líneas + `join`; `resumen_ventas` reutiliza `total_vendido()`. | Biblioteca estándar en lugar de algoritmos hechos a mano (`sorted` es estable, igual que la burbuja) y sin duplicación. Se descartaron 4 simplificaciones "obvias" que cambiaban el comportamiento: `dict.get(c, 0) +` (convierte `True` en `1`), calcular `texto.lower()` antes del bucle, f-strings para unir código y nombre, y `sum()`. Comparación contra R8: 45 000 llamadas idénticas. | ✅ 20/20 · caract. 12/12 · ruff 0 |

> Agrega más filas si realizas más de 5 refactorizaciones.

## Incidencias

Pruebas que fallaron durante alguna refactorización, su causa y cómo se corrigió.

| Refactorización | Intento | Pruebas que fallaron | Pruebas que pasaron | Causa | Corrección |
|---|---|---|---|---|---|
| R7 | 1 | Ninguna prueba falló; **ruff** marcó 3 errores en lugar de 2: `E501` (línea de 89 > 88 caracteres) en `reportes.py` | 20/20 · 12/12 | Al renombrar `aux` → `unidades_por_codigo`, una línea de `mas_vendidos` superó el largo máximo. No cambia el comportamiento, pero viola el estilo que exige el reto | Se reescribió con `+=` (equivalente para números) y se repitieron las tres verificaciones: 20/20 · 12/12 · ruff 2 |

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
