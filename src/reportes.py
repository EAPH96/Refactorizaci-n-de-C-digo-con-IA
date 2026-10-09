"""Reportes de la tienda: inventario, ventas y mas vendidos."""

import gestor

STOCK_MINIMO = 5
TOP_MAS_VENDIDOS = 3


def formatear_dinero(monto):
    # le da formato de dinero al numero
    return "$" + str(round(monto, 2))


def _es_stock_bajo(producto):
    """Indica si el producto tiene menos unidades que el stock minimo."""
    return producto["stock"] < STOCK_MINIMO


def productos_stock_bajo():
    """Regresa la lista de productos con stock por debajo del minimo."""
    return [
        producto for producto in gestor.INVENTARIO.values()
        if _es_stock_bajo(producto)
    ]


def reporte_inventario():
    """Arma el reporte del inventario, lo imprime y lo regresa como texto."""
    lineas = ["===== INVENTARIO ====="]
    # acumulado en bucle (no sum()): en Python >= 3.12 sum() usa suma
    # compensada y podria dar un resultado distinto
    valor_total = 0
    for producto in gestor.INVENTARIO.values():
        # concatenacion con + (no f-string): conserva el TypeError si el
        # codigo o el nombre no son texto
        linea = (
            producto["codigo"] + " | " + producto["nombre"] + " | "
            + formatear_dinero(producto["precio"])
            + " | stock: " + str(producto["stock"])
        )
        if _es_stock_bajo(producto):
            linea = linea + "  <-- STOCK BAJO"
        lineas.append(linea)
        valor_total = valor_total + producto["precio"] * producto["stock"]
    lineas.append("Valor total del inventario: " + formatear_dinero(valor_total))
    texto = "\n".join(lineas) + "\n"
    print(texto)
    return texto


def total_vendido():
    """Suma el total (con IVA) de todas las ventas registradas."""
    total = 0
    for venta in gestor.VENTAS:
        total = total + venta["total"]
    return round(total, 2)


def mas_vendidos(n=TOP_MAS_VENDIDOS):
    """Regresa los n productos mas vendidos como lista de (codigo, unidades)."""
    unidades_por_codigo = {}
    for venta in gestor.VENTAS:
        codigo = venta["codigo"]
        # if/else (no dict.get(codigo, 0) + ...): sumar a 0 convertiria una
        # cantidad True en el entero 1
        if codigo in unidades_por_codigo:
            unidades_por_codigo[codigo] += venta["cantidad"]
        else:
            unidades_por_codigo[codigo] = venta["cantidad"]
    # sorted es estable: en empates conserva el orden de la primera venta
    ranking = sorted(
        unidades_por_codigo.items(), key=lambda par: par[1], reverse=True
    )
    return ranking[:n]


def resumen_ventas():
    """Arma el resumen de ventas del dia, lo imprime y lo regresa."""
    lineas = ["===== RESUMEN DE VENTAS ====="]
    for venta in gestor.VENTAS:
        lineas.append(
            "Folio " + str(venta["folio"]) + ": " + venta["nombre"]
            + " x" + str(venta["cantidad"]) + " = "
            + formatear_dinero(venta["total"])
        )
    lineas.append("Numero de ventas: " + str(len(gestor.VENTAS)))
    lineas.append("Total del dia: " + formatear_dinero(total_vendido()))
    texto = "\n".join(lineas) + "\n"
    print(texto)
    return texto
