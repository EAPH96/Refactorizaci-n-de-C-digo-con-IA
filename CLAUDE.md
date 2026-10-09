# CLAUDE.md

Guía para Claude Code en este repositorio. Léela completa antes de proponer o
editar código. Si algo aquí contradice a `README.md`, **manda el README**.

---

## 1. Qué es este proyecto

Gestor de inventario y ventas de consola para la tienda "La Esquina", escrito
en Python 3.10+ **sin dependencias de ejecución**. Permite dar de alta
productos, registrar ventas (descuentos por volumen, descuento VIP, IVA 16 %,
folio y ticket), cotizar, ver reportes y guardar/cargar el estado en JSON.

Es un **reto académico de refactorización**: el código funciona (20/20 tests)
pero tiene malas prácticas sembradas a propósito. El objetivo es **mejorar la
calidad sin cambiar el comportamiento**, una refactorización a la vez, y
documentar cada paso.

- Diagnóstico completo: `Documentación/00-investigacion/investigacion.md`
  (code smells `CS-xx`, problemas `Q-xx`, plan `R1…R9`, contrato de comportamiento).
- Plan de refactorización y prompts por fase: `Documentación/02-plan-refactorizacion/plan-refactorizacion.md`.
- Stack tecnológico: `Documentación/config.yaml`.
- `Documentación/` es **local** (está en `.gitignore`): no forma parte del PR.

## 2. Comandos

```bash
python -m venv .venv
.venv\Scripts\activate            # Windows (PowerShell)
source .venv/bin/activate         # macOS / Linux / Git Bash
pip install -r requirements.txt

pytest -v                         # suite oficial: 20/20 SIEMPRE
pytest Documentación/caracterizacion -v   # caracterización: 12/12 SIEMPRE
ruff check src                    # meta final: 0 errores (línea base: 20)
ruff check src --statistics       # conteo por regla
cd src && python main.py          # app interactiva (ver advertencia Q-01)
python Documentación/documentacion.py   # visor HTML en vivo de la documentación
```

Ejecuta las **tres** verificaciones (`pytest`, caracterización y `ruff check src`)
**después de cada refactorización**, no solo al final.

La suite de caracterización (`Documentación/caracterizacion/`) compara el
comportamiento contra `snapshot_linea_base.json`, capturado antes de R1: ticket,
reportes, menú, archivo JSON, mensajes de error y casos límite que `tests/` no
cubre. **Nunca** regeneres el snapshot (`escenarios.py --actualizar`) para hacer
pasar una prueba: si falla, el cambio alteró el comportamiento.

## 3. Reglas inviolables

1. **NUNCA** modificar nada en `tests/` ni `pyproject.toml`. Ni para "arreglar"
   un test, ni para silenciar una regla de ruff (`# noqa` tampoco).
2. Conservar los nombres `agregarProducto` y `buscarProducto` (los usan los tests;
   están exentos de N802 en `pyproject.toml`).
3. No mover ni renombrar `src/gestor.py`, `src/almacen.py`, `src/reportes.py`.
   `tests/conftest.py` agrega `src/` a `sys.path` y los importa como módulos
   sueltos (`import gestor`). Sí se pueden **crear** módulos nuevos en `src/`.
   No convertir `src/` en paquete ni usar imports relativos.
4. El **comportamiento observable** queda idéntico (ver §5).
5. Compatible con **Python 3.10**: nada de `typing.Self`, `StrEnum`, `tomllib`,
   `ExceptionGroup`, `except*`, ni otras APIs 3.11+. (Localmente hay 3.14:
   que funcione aquí no prueba que funcione en 3.10.)
6. No agregar dependencias a `requirements.txt`.
7. Si un test falla tras un cambio, **el cambio alteró el comportamiento**:
   revertir o corregir el código de `src/`, nunca el test.
8. Defectos de comportamiento detectados (Q-01…Q-11 de la investigación):
   **reportarlos, no corregirlos** sin aprobación explícita.

## 4. Arquitectura

```
main.py ──► gestor.py ◄── almacen.py      (almacen LEE y ESCRIBE el estado de gestor)
   │            ▲
   └──► reportes.py (solo lee el estado de gestor)
```

| Módulo | Responsabilidad | Estado global que toca |
|---|---|---|
| `gestor.py` | Productos, ventas, cotización; dueño del estado | `INVENTARIO`, `VENTAS`, `contador_ventas`, `ultimo_error` |
| `almacen.py` | Persistencia JSON | Lee y escribe todo lo anterior |
| `reportes.py` | Stock bajo, inventario, totales, más vendidos | Lee `INVENTARIO`, `VENTAS` |
| `main.py` | Menú de consola (`input`/`print`) | Lee `ultimo_error` |

Los errores se comunican regresando `False`/`None` y dejando el motivo en
`gestor.ultimo_error`. **No** cambiar a excepciones: rompe el contrato.

## 5. Contrato de comportamiento (no romper)

**API usada por los tests**
- `gestor`: `INVENTARIO`, `VENTAS`, `reiniciar_sistema`, `agregarProducto`,
  `eliminar_producto`, `actualizar_stock`, `buscarProducto`, `registrar_venta`, `cotizar`.
- `almacen`: `guardar_datos`, `cargar_datos`.
- `reportes`: `productos_stock_bajo`, `total_vendido`, `mas_vendidos`, `reporte_inventario`.

**Estado**
- `INVENTARIO` (dict) y `VENTAS` (list) se mutan **en sitio** (`clear()`,
  `[k] = v`, `append`). Nunca reasignarlos (`INVENTARIO = {}` rompe a quien
  conserve una referencia).
- `gestor.contador_ventas` (antes `contadorVentas`, renombrado en R7) lo leen y
  escriben `gestor.py` y `almacen.py`; si se renombra, actualizar ambos. En el
  JSON se guarda con la clave `"contador"`, que no cambia.

**Valores de retorno**
- `agregarProducto`, `eliminar_producto`, `actualizar_stock`, `guardar_datos`,
  `cargar_datos` → `True` / `False` (literalmente: los tests usan `is True`).
- `registrar_venta` → `dict` o `None`; `cotizar` → `float` o `None`.
- `mas_vendidos(n=3)` → `list[tuple[str, int]]` descendente; empates en orden de
  primera aparición (estable).
- `buscarProducto` y `productos_stock_bajo` regresan los **mismos dicts** del inventario.

**Orden de validaciones y mensajes de `ultimo_error`** (textos exactos, sin acentos)
- `agregarProducto`: `codigo vacio` → `el producto ya existe` → `precio invalido` (≤ 0) → `stock invalido` (< 0).
- `registrar_venta`: `codigo vacio` → `producto no existe` → `cantidad invalida` → `stock insuficiente`.
- `cotizar`: `producto no existe` → `cantidad invalida` (no valida código vacío ni stock).
- `eliminar_producto` / `actualizar_stock`: `producto no existe`; `actualizar_stock`: `el stock no puede quedar negativo`.
- `cargar_datos`: `el archivo no existe`, `archivo corrupto`.

**Reglas de cálculo** (conservar el orden de las operaciones de punto flotante)
```python
subtotal = precio * cantidad
desc = subtotal * 0.10 if subtotal >= 1000 else subtotal * 0.05 if subtotal >= 500 else 0
if cliente_empieza_con_VIP and subtotal - desc > 200:   # solo registrar_venta
    desc = desc + subtotal * 0.02                      # 2 % del SUBTOTAL
base = subtotal - desc
impuesto = base * 0.16
total = round(base + impuesto, 2)                      # NO usar base * 1.16
# Se guardan round(subtotal, 2), round(desc, 2), round(impuesto, 2) y total.
```
- `cotizar` **no** aplica VIP. Su total debe coincidir con el de la venta para
  clientes no VIP.
- Stock bajo: `stock < 5` (estricto).
- Reemplazar un bucle `t = t + x` por `sum()` puede cambiar el resultado en
  Python ≥ 3.12 (suma compensada). Si se hace, justificarlo y verificarlo.

**Formatos de salida**
- Claves de producto, en orden: `codigo, nombre, precio, stock`.
- Claves de venta, en orden: `folio, codigo, nombre, cantidad, subtotal,
  descuento, impuesto, total, cliente, fecha, ticket` (el orden se ve en el JSON).
- `fecha`: `datetime.now().strftime("%Y-%m-%d %H:%M:%S")`.
- JSON: claves `inventario`, `ventas`, `contador`; `indent=2`, `ensure_ascii=False`.
- Ticket (la línea `Descuento` solo aparece si `desc > 0`):
  ```text
  TIENDA LA ESQUINA
  ----------------------------
  Folio: 1
  Café x2
  Subtotal: $20.0
  IVA: $3.2
  TOTAL: $23.2
  ```
- Dinero en reportes: `"$" + str(round(v, 2))` → `$23.2`, **no** `$23.20`.
- `reporte_inventario()` y `resumen_ventas()` hacen `print(texto)` **y** `return texto`.
- Textos del menú de `main.py` y mensajes de consola: idénticos, carácter por carácter.

## 6. Convenciones y guía de estilo

### Generales
- PEP 8, línea máx. 88 (lo valida ruff). Indentación de 4 espacios.
- Identificadores en **español** y `snake_case`; constantes en `MAYUSCULAS_SNAKE`.
  Excepción: `agregarProducto`, `buscarProducto`.
- Nombres que expliquen la intención: nada de `x`, `aux`, `temp2`, `t`, `hacer_cosa`.
  Variables de bucle cortas solo si el contexto es obvio (`for codigo, producto in ...`).
- Docstring en español en toda función pública: una línea de resumen en
  imperativo/descriptivo; detalle si regresa sentinelas (`None`/`False`).
- Type hints con sintaxis 3.10: `str | None`, `list[dict]`, `dict[str, int]`.
  Para los registros usar alias simples (`Producto = dict[str, Any]`) en vez de
  clases nuevas: el contrato exige `dict`.
- Sin cabecera `# -*- coding: utf-8 -*-` (UP009).
- Imports ordenados: estándar → terceros → locales (`gestor`, `almacen`, `reportes`), ruff `I`.
- Archivos siempre con `with open(..., encoding="utf-8")`.
- Comentarios: explican el *porqué*, no el *qué*. Eliminar comentarios que
  excusan el código ("por si acaso", "hace de todo").
- Nada de código comentado ni funciones sin uso: Git guarda la historia.

### Ejemplos (antes → después, preservando comportamiento)

**Números mágicos → constantes con nombre**
```python
# Antes
if aux >= 1000:
    desc = aux * 0.10

# Después
UMBRAL_DESCUENTO_ALTO = 1000
TASA_DESCUENTO_ALTO = 0.10
if subtotal >= UMBRAL_DESCUENTO_ALTO:
    descuento = subtotal * TASA_DESCUENTO_ALTO
```

**Pirámide de `if` → cláusulas de guarda** (mismo orden de validación)
```python
# Después
if codigo is None or codigo == "":
    ultimo_error = "codigo vacio"
    return None
if codigo not in INVENTARIO:
    ultimo_error = "producto no existe"
    return None
if cantidad is None or cantidad <= 0:
    ultimo_error = "cantidad invalida"
    return None
if INVENTARIO[codigo]["stock"] < cantidad:
    ultimo_error = "stock insuficiente"
    return None
```

**`if` anidados → condición única**
```python
# Antes
if cliente != "" and cliente is not None:
    if len(cliente) >= 3:
        if cliente[0:3] == "VIP":
            if aux - desc > 200:
                desc = desc + aux * 0.02
# Después (equivalente para str y None)
if cliente and cliente.startswith(PREFIJO_VIP) and subtotal - descuento > MINIMO_VIP:
    descuento += subtotal * TASA_VIP
```

**Archivos con context manager**
```python
# Antes
f = open(ruta, "w", encoding="utf-8")
json.dump(d, f, indent=2, ensure_ascii=False)
f.close()
# Después
with open(ruta, "w", encoding="utf-8") as archivo:
    json.dump(datos, archivo, indent=2, ensure_ascii=False)
```

**Construcción de dicts** (mismo orden de claves)
```python
# Después
INVENTARIO[codigo] = {"codigo": codigo, "nombre": nombre, "precio": precio, "stock": stock}
```

**Algoritmo estándar** (`sorted` es estable igual que la burbuja actual)
```python
return sorted(unidades.items(), key=lambda par: par[1], reverse=True)[:n]
```

### ❌ Cambios que parecen mejoras pero rompen el contrato
```python
f"${v:.2f}"                    # cambia "$23.2" por "$23.20"
total = round(base * 1.16, 2)  # otro orden de operaciones en flotante
INVENTARIO = {}                # reasigna en vez de mutar en sitio
raise ValueError("codigo vacio")  # los llamadores esperan None/False
cotizar(codigo, cantidad, cliente)  # cambia la firma y la regla de negocio
```

## 7. Flujo de trabajo por refactorización

Cada fase sigue **Analyze → Refactor → Verify → Document** (detalle y prompts
en el plan, `Documentación/02-plan-refactorizacion/`):

1. **Analyze (sin editar):** leer el código afectado; listar smells (`CS-xx`),
   reglas ruff y los invariantes de §5 que se tocan; proponer el cambio y su
   riesgo. **Detenerse y esperar visto bueno.**
2. **Refactor:** editar solo lo de esa fase (una refactorización por vez, sin
   mezclar). Código solo en `src/`.
3. **Verify:** `pytest -v`, `pytest Documentación/caracterizacion -v` y
   `ruff check src --statistics`. Revisar el diff contra §5 (auto-revisión).
4. **Document:** ver §8.
5. **Commit atómico** en la rama `refactorizacion`, en español
   (`refactor(gestor): extrae cálculo de descuentos compartido (R3)`), solo
   cuando la persona lo pida.

### Protocolo cuando una prueba falla

1. **Detenerse.** No iniciar otra refactorización con pruebas en rojo.
2. **Registrar** qué suite y qué pruebas fallaron (nombre exacto) y cuáles pasaron.
3. **Diagnosticar la causa raíz**: qué línea del diff viola qué invariante de §5;
   reproducir con el caso mínimo. Nunca culpar al test ni modificarlo.
4. **Documentar** el intento en `RXX-*.md` (sección *Incidencias*) y en
   `docs/bitacora.md` (fila + sección *Incidencias*): pruebas que fallaron, causa
   y corrección propuesta.
5. **Corregir el código de `src/`** y volver a correr las tres verificaciones.
6. Repetir hasta tener todo en verde. Tras **3 intentos fallidos**: revertir la
   fase (`git checkout -- src/`), explicar y replantear con la persona.

## 8. Documentación del proceso

```
docs/                                 # ENTREGABLES
├── bitacora.md                       # Una fila por refactorización + resumen de reflexión
└── reflexion.md                      # Aprendizajes y conclusiones completas
Documentación/                        # DOCUMENTACIÓN LOCAL (en .gitignore, no va al PR)
├── documentacion.py                  # Visor HTML en vivo (stdlib). El .md es la fuente.
├── index.html                        # (generado) índice
├── bitacora.html, reflexion.html     # (generados) vistas de docs/*.md
├── plantillas/refactorizacion.md     # Plantilla para cada refactorización
├── 00-investigacion/                 # Investigación + prompt + notas del usuario
├── 01-configuracion-entorno/         # Configuración + prompt + notas del usuario
├── 02-plan-refactorizacion/          # Plan, técnicas y prompts por fase
├── caracterizacion/                  # Suite golden master (snapshot de línea base)
├── config.yaml                       # Stack tecnológico
└── refactorizaciones/                # RXX-<slug>.md (+ .html generado)
```

- Los `.html` **leen su `.md` al abrirse** (servidos por `documentacion.py`
  en `http://127.0.0.1`) y se actualizan solos al guardar el `.md`. Abiertos
  como `file://` muestran la última instantánea incrustada.
- Nunca editar un `.html` a mano.

Al terminar **cada** refactorización:
1. Copiar `Documentación/plantillas/refactorizacion.md` →
   `Documentación/refactorizaciones/RXX-<slug>.md` y llenar las secciones (IA):
   prompt, qué se realizó, plan, qué cambió (tabla), antes/después,
   justificación, comportamiento preservado, resultados de pruebas por suite
   e incidencias (si las hubo).
2. **No tocar** las secciones `## Notas del usuario`: las llena la persona a
   mano. Si se edita un `.md` que ya tiene notas, conservarlas íntegras.
   Tampoco las `#### Notas del usuario` dentro de cada corrección.
3. Ejecutar `python Documentación/documentacion.py --generar`.
4. Agregar la fila correspondiente en `docs/bitacora.md` (prompt, cambio,
   justificación, resultado de tests). En *Tests OK* usar el formato
   `✅ 20/20 · caract. 12/12 · ruff N`; si hubo fallos, anotarlos también en la
   sección *Incidencias* de la bitácora. `docs/` sí va al PR: no enlazar rutas
   de `Documentación/` como si el revisor pudiera abrirlas.

### Correcciones del usuario

Si después del prompt principal de una fase la persona pide modificar el
resultado (o hace un cambio manual), regístralo en la sección
`## Correcciones posteriores al prompt principal` del documento de esa fase,
con el siguiente número: `### Corrección N — <título>`, tabla (fecha, tipo,
archivos, verificación), `#### Instrucción del usuario` (texto tal cual),
`#### Qué se cambió` y `#### Notas del usuario` vacía. Agrega además una fila en
*Correcciones a la IA* de `docs/bitacora.md`. Detalle en §5.5 del plan.

### Evidencias

Cada documento de fase tiene una sección `## Evidencias` con capturas o
adjuntos que la persona sube desde el visor (panel *📎 Agregar evidencia*).
Los archivos viven en `Documentación/evidencias/<documento>/`. **No edites ni
borres** las entradas de esa sección; al crear un `RXX-*.md` desde la
plantilla, conserva la sección vacía.

Los documentos `RXX-*.md` se muestran como **pestañas** en
`Documentación/02-plan-refactorizacion/plan-refactorizacion.html`; respeta los
nombres de archivo de la tabla del §7 del plan para que cada uno caiga en su pestaña.

## 9. Archivos que no debes leer ni editar

- Ver `.claudeignore` (entornos virtuales, cachés, datos generados, HTML generado).
- `Documentación/**/*.html` se generan: edita el `.md` correspondiente.
- `src/datos_ejemplo.json`, si existe, es un archivo generado por ejecutar la
  app desde `src/` (Q-01); no es fuente de datos.
