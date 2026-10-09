"""Modulo principal del gestor de inventario y ventas de "La Esquina".

Aqui vive casi toda la logica del negocio. Historicamente este archivo
lo fueron parchando varias personas, asi que hay de todo un poco.
"""

from datetime import datetime

# ---------------------------------------------------------------
# Reglas de negocio
# ---------------------------------------------------------------
UMBRAL_DESCUENTO_ALTO = 1000
TASA_DESCUENTO_ALTO = 0.10
UMBRAL_DESCUENTO_MEDIO = 500
TASA_DESCUENTO_MEDIO = 0.05
PREFIJO_VIP = "VIP"
MONTO_MINIMO_VIP = 200
TASA_DESCUENTO_VIP = 0.02
TASA_IVA = 0.16
FORMATO_FECHA = "%Y-%m-%d %H:%M:%S"
ENCABEZADO_TICKET = "TIENDA LA ESQUINA"
SEPARADOR_TICKET = "-" * 28

# ---------------------------------------------------------------
# Estado global de la aplicacion (inventario, ventas y contadores)
# ---------------------------------------------------------------
INVENTARIO = {}
VENTAS = []
contador_ventas = 0
ultimo_error = ""


def calcular_descuento(subtotal, cliente=""):
    """Descuento por volumen y, si el cliente es VIP, el extra correspondiente."""
    descuento = 0
    if subtotal >= UMBRAL_DESCUENTO_ALTO:
        descuento = subtotal * TASA_DESCUENTO_ALTO
    elif subtotal >= UMBRAL_DESCUENTO_MEDIO:
        descuento = subtotal * TASA_DESCUENTO_MEDIO
    # el extra VIP solo aplica si la compra (ya con descuento) pasa del minimo
    if (
        cliente
        and cliente.startswith(PREFIJO_VIP)
        and subtotal - descuento > MONTO_MINIMO_VIP
    ):
        descuento = descuento + subtotal * TASA_DESCUENTO_VIP
    return descuento


def calcular_impuesto(base):
    """IVA sobre la base (subtotal menos descuentos)."""
    return base * TASA_IVA


def reiniciar_sistema():
    """Borra todo el estado del sistema (inventario, ventas y folios)."""
    global contador_ventas, ultimo_error
    INVENTARIO.clear()
    VENTAS.clear()
    contador_ventas = 0
    ultimo_error = ""


def agregarProducto(codigo, nombre, precio, stock):
    # valida los datos y da de alta un producto en el inventario
    global ultimo_error
    if codigo is None or codigo == "":
        ultimo_error = "codigo vacio"
        return False
    if codigo in INVENTARIO:
        ultimo_error = "el producto ya existe"
        return False
    if precio <= 0:
        ultimo_error = "precio invalido"
        return False
    if stock < 0:
        ultimo_error = "stock invalido"
        return False
    INVENTARIO[codigo] = {
        "codigo": codigo,
        "nombre": nombre,
        "precio": precio,
        "stock": stock,
    }
    return True


def eliminar_producto(codigo):
    """Quita un producto del inventario. Regresa False si no existe."""
    global ultimo_error
    if codigo in INVENTARIO:
        del INVENTARIO[codigo]
        return True
    ultimo_error = "producto no existe"
    return False


def actualizar_stock(codigo, cantidad):
    """Suma unidades al stock (o resta si la cantidad es negativa)."""
    global ultimo_error
    if codigo not in INVENTARIO:
        ultimo_error = "producto no existe"
        return False
    stock_nuevo = INVENTARIO[codigo]["stock"] + cantidad
    if stock_nuevo < 0:
        ultimo_error = "el stock no puede quedar negativo"
        return False
    INVENTARIO[codigo]["stock"] = stock_nuevo
    return True


def buscarProducto(texto):
    # busca productos cuyo nombre contenga el texto (sin importar mayusculas)
    # texto.lower() se evalua dentro de la comprension (no antes): con el
    # inventario vacio, buscarProducto(None) regresa [] en lugar de fallar
    return [
        producto for producto in INVENTARIO.values()
        if texto.lower() in producto["nombre"].lower()
    ]


def _validar_venta(codigo, cantidad):
    """Valida una venta; si no procede deja el motivo en ultimo_error.

    Las validaciones van en este orden y se detienen en la primera que falla.
    Se niegan las condiciones originales (``not cantidad > 0``) en lugar de
    invertirlas (``cantidad <= 0``) porque no son equivalentes con NaN.
    """
    global ultimo_error
    if codigo is None or codigo == "":
        ultimo_error = "codigo vacio"
        return False
    if codigo not in INVENTARIO:
        ultimo_error = "producto no existe"
        return False
    if cantidad is None or not cantidad > 0:
        ultimo_error = "cantidad invalida"
        return False
    if not INVENTARIO[codigo]["stock"] >= cantidad:
        ultimo_error = "stock insuficiente"
        return False
    return True


def _generar_ticket(venta, descuento):
    """Texto del ticket de una venta registrada.

    `descuento` es el monto sin redondear: la linea de descuento solo aparece
    si es mayor que cero.
    """
    lineas = [
        ENCABEZADO_TICKET,
        SEPARADOR_TICKET,
        f"Folio: {venta['folio']}",
        f"{venta['nombre']} x{venta['cantidad']}",
        f"Subtotal: ${venta['subtotal']}",
    ]
    if descuento > 0:
        lineas.append(f"Descuento: -${venta['descuento']}")
    lineas.append(f"IVA: ${venta['impuesto']}")
    lineas.append(f"TOTAL: ${venta['total']}")
    return "\n".join(lineas) + "\n"


def registrar_venta(codigo, cantidad, cliente=""):
    """Registra una venta: valida, calcula montos, descuenta stock y genera el ticket.

    Si algo falla regresa None y deja el motivo en ultimo_error.
    """
    global contador_ventas
    if not _validar_venta(codigo, cantidad):
        return None
    producto = INVENTARIO[codigo]
    subtotal = producto["precio"] * cantidad
    descuento = calcular_descuento(subtotal, cliente)
    base = subtotal - descuento
    impuesto = calcular_impuesto(base)
    total = round(base + impuesto, 2)
    producto["stock"] = producto["stock"] - cantidad
    contador_ventas = contador_ventas + 1
    venta = {
        "folio": contador_ventas,
        "codigo": codigo,
        "nombre": producto["nombre"],
        "cantidad": cantidad,
        "subtotal": round(subtotal, 2),
        "descuento": round(descuento, 2),
        "impuesto": round(impuesto, 2),
        "total": total,
        "cliente": cliente,
        "fecha": datetime.now().strftime(FORMATO_FECHA),
    }
    venta["ticket"] = _generar_ticket(venta, descuento)
    VENTAS.append(venta)
    return venta


def cotizar(codigo, cantidad):
    """Calcula cuanto costaria una compra sin registrar la venta."""
    global ultimo_error
    if codigo not in INVENTARIO:
        ultimo_error = "producto no existe"
        return None
    if cantidad is None or cantidad <= 0:
        ultimo_error = "cantidad invalida"
        return None
    subtotal = INVENTARIO[codigo]["precio"] * cantidad
    # la cotizacion no recibe cliente: nunca aplica el extra VIP
    descuento = calcular_descuento(subtotal)
    base = subtotal - descuento
    total = base + calcular_impuesto(base)
    return round(total, 2)
