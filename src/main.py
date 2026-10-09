"""Punto de entrada del gestor de tienda (menu interactivo en consola)."""

from collections.abc import Callable

import almacen
import gestor
import reportes

ARCHIVO = "datos_ejemplo.json"
OPCION_SALIR = "8"


def pedir_numero(mensaje: str) -> float:
    """Pide un numero hasta que la persona escriba algo valido."""
    while True:
        respuesta = input(mensaje)
        try:
            return float(respuesta)
        except ValueError:
            print("Eso no es un numero, intenta de nuevo.")


def _agregar_producto() -> None:
    """Opcion 1: pide los datos de un producto y lo da de alta."""
    codigo = input("Codigo: ")
    nombre = input("Nombre: ")
    precio = pedir_numero("Precio: ")
    stock = int(pedir_numero("Stock inicial: "))
    if gestor.agregarProducto(codigo, nombre, precio, stock):
        print("Producto agregado.")
    else:
        print("Error:", gestor.ultimo_error)


def _registrar_venta() -> None:
    """Opcion 2: registra una venta e imprime su ticket."""
    codigo = input("Codigo del producto: ")
    cantidad = int(pedir_numero("Cantidad: "))
    cliente = input("Codigo de cliente (enter si no tiene): ")
    venta = gestor.registrar_venta(codigo, cantidad, cliente)
    if venta is not None:
        print(venta["ticket"])
    else:
        print("Error:", gestor.ultimo_error)


def _cotizar() -> None:
    """Opcion 3: muestra el total estimado de una compra sin registrarla."""
    codigo = input("Codigo del producto: ")
    cantidad = int(pedir_numero("Cantidad: "))
    total = gestor.cotizar(codigo, cantidad)
    if total is not None:
        print("Total estimado (con IVA): $" + str(total))
    else:
        print("Error:", gestor.ultimo_error)


def _mas_vendidos() -> None:
    """Opcion 6: lista los productos mas vendidos."""
    for codigo, unidades in reportes.mas_vendidos():
        print(codigo, "->", unidades, "unidades")


def _alertas_stock_bajo() -> None:
    """Opcion 7: avisa de los productos con stock bajo."""
    bajos = reportes.productos_stock_bajo()
    if len(bajos) == 0:
        print("No hay productos con stock bajo.")
    else:
        for producto in bajos:
            print("OJO:", producto["nombre"], "solo tiene", producto["stock"],
                  "unidades")


def _guardar_y_salir() -> None:
    """Opcion 8: guarda los datos (el ciclo del menu termina despues)."""
    almacen.guardar_datos(ARCHIVO)
    print("Datos guardados. Hasta luego.")


# Tabla de despacho: clave -> (texto en el menu, accion). El orden de
# insercion es el orden en que se muestran las opciones.
OPCIONES: dict[str, tuple[str, Callable[[], object]]] = {
    "1": ("Agregar producto", _agregar_producto),
    "2": ("Registrar venta", _registrar_venta),
    "3": ("Cotizar", _cotizar),
    "4": ("Reporte de inventario", reportes.reporte_inventario),
    "5": ("Resumen de ventas", reportes.resumen_ventas),
    "6": ("Mas vendidos", _mas_vendidos),
    "7": ("Alertas de stock bajo", _alertas_stock_bajo),
    OPCION_SALIR: ("Guardar y salir", _guardar_y_salir),
}


def _cargar_datos_iniciales() -> None:
    """Carga el archivo de datos si existe."""
    if almacen.hay_archivo(ARCHIVO):
        almacen.cargar_datos(ARCHIVO)
        print("Datos cargados de", ARCHIVO)


def _mostrar_opciones() -> None:
    """Imprime el menu de opciones."""
    print("")
    for clave, (etiqueta, _) in OPCIONES.items():
        print(f"{clave}) {etiqueta}")


def menu() -> None:
    """Ciclo principal del menu de consola."""
    print("Bienvenido al gestor de la tienda La Esquina")
    _cargar_datos_iniciales()
    while True:
        _mostrar_opciones()
        opcion = input("Opcion: ")
        if opcion not in OPCIONES:
            print("Opcion no valida.")
            continue
        _, accion = OPCIONES[opcion]
        accion()
        if opcion == OPCION_SALIR:
            break


if __name__ == "__main__":
    menu()
