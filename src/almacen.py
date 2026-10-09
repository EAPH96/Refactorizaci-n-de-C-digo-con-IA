"""Persistencia del gestor: carga y guardado de datos en JSON."""

import json
import os

import gestor


def guardar_datos(ruta: str) -> bool:
    """Guarda el inventario, las ventas y el folio actual en un JSON."""
    datos = {
        "inventario": gestor.INVENTARIO,
        "ventas": gestor.VENTAS,
        "contador": gestor.contador_ventas,
    }
    with open(ruta, "w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, indent=2, ensure_ascii=False)
    return True


def cargar_datos(ruta: str) -> bool:
    """Lee el archivo JSON y deja los datos en el estado global.

    Regresa False si el archivo no existe o esta corrupto.
    """
    if not os.path.exists(ruta):
        gestor.ultimo_error = "el archivo no existe"
        return False
    with open(ruta, encoding="utf-8") as archivo:
        try:
            datos = json.load(archivo)
        except Exception:
            gestor.ultimo_error = "archivo corrupto"
            return False
    gestor.INVENTARIO.clear()
    # bucle (no dict.update): con un "inventario" mal formado, como la lista
    # ["ab"], update cargaria {"a": "b"} en silencio en vez de fallar
    for codigo in datos["inventario"]:
        gestor.INVENTARIO[codigo] = datos["inventario"][codigo]
    gestor.VENTAS.clear()
    gestor.VENTAS.extend(datos["ventas"])
    gestor.contador_ventas = datos.get("contador", 0)
    return True


def hay_archivo(ruta: str) -> bool:
    """Indica si ya existe el archivo de datos."""
    return os.path.exists(ruta)
