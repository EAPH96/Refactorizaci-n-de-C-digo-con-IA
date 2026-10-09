"""Escenarios de caracterización (golden master) del comportamiento ACTUAL.

Cada función ejecuta el sistema y regresa datos serializables a JSON con todo
lo observable: valores de retorno, mensajes de `ultimo_error`, texto impreso,
tickets y el archivo JSON guardado. Las fechas se enmascaran porque cambian.

Solo usa la API pública que sobrevive a TODO el plan de refactorización
(R1-R9): nada de `calcular_descuento_viejo`, `reporteViejoCSV`,
`contadorVentas` ni `hayArchivo`, que se eliminan o renombran a propósito.

Uso:
    python tests_caracterizacion/escenarios.py --actualizar
        Regenera snapshot_linea_base.json. SOLO en la línea base (antes de R1)
        o cuando un cambio de comportamiento haya sido aprobado explícitamente.
"""

from __future__ import annotations

import builtins
import contextlib
import io
import json
import os
import re
import shutil
import sys
import tempfile
from collections.abc import Callable
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
SRC = RAIZ / "src"
SNAPSHOT = AQUI / "snapshot_linea_base.json"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import almacen  # noqa: E402
import gestor  # noqa: E402
import reportes  # noqa: E402

FECHA = re.compile(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}")


def _sin_fecha(valor):
    """Copia profunda con las fechas reemplazadas por <FECHA>."""
    texto = json.dumps(valor, ensure_ascii=False)
    return json.loads(FECHA.sub("<FECHA>", texto))


def _llamar(funcion: Callable, *args, etiqueta: str | None = None) -> dict:
    """Ejecuta una función del gestor y registra retorno, error y salida.

    `etiqueta` sustituye a los argumentos en el registro (p. ej. rutas temporales).
    """
    gestor.ultimo_error = ""
    salida = io.StringIO()
    with contextlib.redirect_stdout(salida):
        resultado = funcion(*args)
    llamada = f"({etiqueta})" if etiqueta else repr(args)
    return {
        "llamada": f"{funcion.__name__}{llamada}",
        "retorno": _sin_fecha(resultado),
        "tipo": type(resultado).__name__,
        "ultimo_error": gestor.ultimo_error,
        "impreso": salida.getvalue(),
    }


def _catalogo_basico() -> None:
    gestor.agregarProducto("A1", "Café de grano", 100.0, 500)
    gestor.agregarProducto("A2", "Azúcar", 10.0, 500)
    gestor.agregarProducto("B1", "Chocolate", 78.9, 500)
    gestor.agregarProducto("B2", "Galletas", 33.33, 500)
    gestor.agregarProducto("C1", "Leche", 50.0, 500)


def escenario_ventas() -> list[dict]:
    """Ventas en todos los rangos de descuento y variantes de cliente."""
    gestor.reiniciar_sistema()
    _catalogo_basico()
    casos = [
        ("A2", 2, ""),            # sin descuento
        ("A1", 4, ""),            # 400: justo debajo del 5 %
        ("A1", 5, ""),            # 500: límite exacto del 5 %
        ("A1", 6, ""),            # 600: 5 %
        ("A1", 10, ""),           # 1000: límite exacto del 10 %
        ("A1", 20, ""),           # 2000: 10 %
        ("A1", 6, "VIP007"),      # VIP con compra > 200 tras descuento
        ("C1", 4, "VIP1"),        # VIP: 200 - 0 = 200, NO supera 200
        ("C1", 5, "VIP1"),        # VIP: 250 > 200
        ("A1", 20, "VIP9"),       # VIP + 10 %
        ("A1", 3, "VI"),          # cliente corto, no es VIP
        ("A1", 3, "vip007"),      # minúsculas, no es VIP
        ("A1", 3, "XVIP"),        # VIP no al inicio
        ("A1", 1, None),          # cliente None
        ("B1", 7, ""),            # flotantes: 552.3
        ("B2", 3, ""),            # flotantes: 99.99
        ("B2", 31, "VIP2"),       # flotantes + VIP + 10 %
    ]
    return [_llamar(gestor.registrar_venta, *caso) for caso in casos]


def escenario_errores() -> list[dict]:
    """Cada validación con su mensaje, en el orden en que se evalúan."""
    gestor.reiniciar_sistema()
    gestor.agregarProducto("A1", "Café", 10.0, 5)
    llamadas = [
        (gestor.agregarProducto, "", "X", 1.0, 1),
        (gestor.agregarProducto, None, "X", 1.0, 1),
        (gestor.agregarProducto, "A1", "X", 1.0, 1),
        (gestor.agregarProducto, "A2", "X", 0, 1),
        (gestor.agregarProducto, "A2", "X", -1.0, 1),
        (gestor.agregarProducto, "A2", "X", 1.0, -1),
        (gestor.agregarProducto, "A3", "Stock cero", 1.0, 0),
        (gestor.registrar_venta, "", 1),
        (gestor.registrar_venta, None, 1),
        (gestor.registrar_venta, "ZZ", 1),
        (gestor.registrar_venta, "ZZ", 0),
        (gestor.registrar_venta, "A1", 0),
        (gestor.registrar_venta, "A1", -2),
        (gestor.registrar_venta, "A1", None),
        (gestor.registrar_venta, "A1", 6),
        (gestor.cotizar, "", 1),
        (gestor.cotizar, "ZZ", 0),
        (gestor.cotizar, "A1", 0),
        (gestor.cotizar, "A1", None),
        (gestor.cotizar, "A1", 999),
        (gestor.eliminar_producto, "ZZ"),
        (gestor.actualizar_stock, "ZZ", 1),
        (gestor.actualizar_stock, "A1", -6),
        (gestor.actualizar_stock, "A1", -5),
        (gestor.eliminar_producto, "A3"),
    ]
    resultado = [_llamar(f, *args) for f, *args in llamadas]
    resultado.append({"inventario_final": _sin_fecha(gestor.INVENTARIO),
                      "ventas": len(gestor.VENTAS)})
    return resultado


def escenario_cotizaciones() -> list[dict]:
    """Cotizar en todos los rangos (sin VIP: cotizar no recibe cliente)."""
    gestor.reiniciar_sistema()
    _catalogo_basico()
    casos = [("A2", 2), ("A1", 5), ("A1", 6), ("A1", 10), ("B1", 7), ("B2", 31)]
    return [_llamar(gestor.cotizar, *caso) for caso in casos]


def escenario_busqueda() -> list[dict]:
    gestor.reiniciar_sistema()
    _catalogo_basico()
    gestor.agregarProducto("A9", "CAFÉ soluble", 60.0, 1)
    return [_llamar(gestor.buscarProducto, t) for t in ("café", "LECHE", "zz", "")]


def escenario_reportes() -> dict:
    """Reportes con ventas, empates en más vendidos y stock bajo."""
    gestor.reiniciar_sistema()
    gestor.agregarProducto("P1", "Uno", 10.0, 50)
    gestor.agregarProducto("P2", "Dos", 20.5, 4)
    gestor.agregarProducto("P3", "Tres", 33.33, 50)
    gestor.agregarProducto("P4", "Cuatro", 1.1, 5)
    gestor.agregarProducto("P5", "Cinco", 7.0, 0)
    vacio = {
        "total_vendido": _llamar(reportes.total_vendido),
        "mas_vendidos": _llamar(reportes.mas_vendidos),
        "resumen_ventas": _llamar(reportes.resumen_ventas),
    }
    for codigo, cantidad in [("P1", 3), ("P3", 5), ("P2", 1), ("P1", 2),
                             ("P4", 3), ("P3", 1), ("P4", 1), ("P2", 3)]:
        gestor.registrar_venta(codigo, cantidad)
    return {
        "sin_ventas": vacio,
        "stock_bajo": _llamar(reportes.productos_stock_bajo),
        "reporte_inventario": _llamar(reportes.reporte_inventario),
        "total_vendido": _llamar(reportes.total_vendido),
        "mas_vendidos_default": _llamar(reportes.mas_vendidos),
        "mas_vendidos_2": _llamar(reportes.mas_vendidos, 2),
        "mas_vendidos_10": _llamar(reportes.mas_vendidos, 10),
        "resumen_ventas": _llamar(reportes.resumen_ventas),
    }


def escenario_persistencia() -> dict:
    """Archivo JSON exacto, recarga, archivo corrupto e inexistente."""
    gestor.reiniciar_sistema()
    _catalogo_basico()
    gestor.registrar_venta("A1", 6, "VIP007")
    gestor.registrar_venta("B1", 7)
    with tempfile.TemporaryDirectory() as carpeta:
        ruta = os.path.join(carpeta, "datos.json")
        guardar = _llamar(almacen.guardar_datos, ruta, etiqueta="datos.json")
        with open(ruta, encoding="utf-8") as archivo:
            contenido = FECHA.sub("<FECHA>", archivo.read())
        gestor.reiniciar_sistema()
        cargar = _llamar(almacen.cargar_datos, ruta, etiqueta="datos.json")
        siguiente = _llamar(gestor.registrar_venta, "A2", 1)
        corrupto = os.path.join(carpeta, "corrupto.json")
        with open(corrupto, "w", encoding="utf-8") as archivo:
            archivo.write("{ esto no es json")
        cargar_corrupto = _llamar(
            almacen.cargar_datos, corrupto, etiqueta="corrupto.json"
        )
        cargar_inexistente = _llamar(
            almacen.cargar_datos,
            os.path.join(carpeta, "no.json"),
            etiqueta="no.json",
        )
    return {
        "guardar": guardar,
        "archivo": contenido,
        "cargar": cargar,
        "venta_tras_recargar": siguiente,
        "cargar_corrupto": cargar_corrupto,
        "cargar_inexistente": cargar_inexistente,
    }


def _ejecutar_menu(entradas: list[str], datos_iniciales: bool) -> dict:
    """Corre main.menu() con entradas simuladas en una carpeta temporal."""
    import main

    gestor.reiniciar_sistema()
    pendientes = iter(entradas)
    salida = io.StringIO()
    original_input = builtins.input
    cwd = os.getcwd()

    def entrada_falsa(mensaje: str = "") -> str:
        valor = next(pendientes)
        print(f"{mensaje}{valor}")
        return valor

    with tempfile.TemporaryDirectory() as carpeta:
        if datos_iniciales:
            shutil.copy(RAIZ / "datos_ejemplo.json", Path(carpeta) / main.ARCHIVO)
        os.chdir(carpeta)
        builtins.input = entrada_falsa
        try:
            with contextlib.redirect_stdout(salida):
                main.menu()
        finally:
            builtins.input = original_input
            os.chdir(cwd)
        guardado = Path(carpeta) / main.ARCHIVO
        archivo = guardado.read_text(encoding="utf-8") if guardado.exists() else None
    return {
        "consola": FECHA.sub("<FECHA>", salida.getvalue()),
        "archivo_guardado": FECHA.sub("<FECHA>", archivo) if archivo else None,
    }


def escenario_menu_vacio() -> dict:
    """Todas las opciones del menú, entradas inválidas y errores."""
    return _ejecutar_menu(
        [
            "1", "A1", "Café", "abc", "100", "10",   # alta (con número inválido)
            "1", "A1", "Otro", "5", "1",             # alta duplicada
            "1", "L1", "Leche", "26", "3",           # alta con stock bajo
            "2", "A1", "6", "VIP007",                # venta VIP
            "2", "A1", "2.9", "",                    # cantidad decimal se trunca
            "2", "ZZ", "1", "",                      # venta con error
            "3", "A1", "6",                          # cotizar
            "3", "ZZ", "1",                          # cotizar con error
            "4", "5", "6", "7",                      # reportes
            "9", "",                                 # opciones inválidas
            "8",                                     # guardar y salir
        ],
        datos_iniciales=False,
    )


def escenario_menu_con_datos() -> dict:
    """Arranque con datos_ejemplo.json, alertas y guardado."""
    return _ejecutar_menu(["7", "4", "6", "2", "B002", "2", "", "7", "8"],
                          datos_iniciales=True)


ESCENARIOS: dict[str, Callable[[], object]] = {
    "ventas": escenario_ventas,
    "errores": escenario_errores,
    "cotizaciones": escenario_cotizaciones,
    "busqueda": escenario_busqueda,
    "reportes": escenario_reportes,
    "persistencia": escenario_persistencia,
    "menu_vacio": escenario_menu_vacio,
    "menu_con_datos": escenario_menu_con_datos,
}


def capturar_todo() -> dict:
    resultado = {nombre: _sin_fecha(f()) for nombre, f in ESCENARIOS.items()}
    gestor.reiniciar_sistema()
    return resultado


if __name__ == "__main__":
    if "--actualizar" not in sys.argv[1:]:
        sys.exit("Usa --actualizar para regenerar el snapshot (solo en la línea base).")
    SNAPSHOT.write_text(
        json.dumps(capturar_todo(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print("Snapshot escrito en", SNAPSHOT.relative_to(RAIZ))
