"""Persistencia del gestor: carga y guardado de datos en JSON."""

import json
import os

import gestor


def guardar_datos(ruta):
    """Guarda el inventario, las ventas y el folio actual en un JSON."""
    d = {
        "inventario": gestor.INVENTARIO,
        "ventas": gestor.VENTAS,
        "contador": gestor.contadorVentas,
    }
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=2, ensure_ascii=False)
    return True


def cargar_datos(ruta):
    """Lee el archivo JSON y deja los datos en el estado global.

    Regresa False si el archivo no existe o esta corrupto.
    """
    if not os.path.exists(ruta):
        gestor.ultimo_error = "el archivo no existe"
        return False
    with open(ruta, encoding="utf-8") as f:
        try:
            d = json.load(f)
        except Exception:
            gestor.ultimo_error = "archivo corrupto"
            return False
    gestor.INVENTARIO.clear()
    # bucle (no dict.update): con un "inventario" mal formado, como la lista
    # ["ab"], update cargaria {"a": "b"} en silencio en vez de fallar
    for k in d["inventario"]:
        gestor.INVENTARIO[k] = d["inventario"][k]
    gestor.VENTAS.clear()
    gestor.VENTAS.extend(d["ventas"])
    gestor.contadorVentas = d.get("contador", 0)
    return True


def hayArchivo(ruta):
    # checa si ya existe el archivo de datos
    return os.path.exists(ruta)
