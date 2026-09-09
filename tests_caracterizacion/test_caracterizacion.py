"""Pruebas de caracterización: el comportamiento debe ser IDÉNTICO a la línea base.

Complementan a tests/ (que no se puede modificar) en las zonas que esa suite no
cubre: ticket, resumen de ventas, formato de dinero, menú de consola, archivo
JSON exacto, mensajes de error, empates y casos límite.

Ejecutar desde la raíz del repositorio:
    pytest tests_caracterizacion -q
"""

import json

import pytest

import almacen
import gestor
import reportes
from escenarios import ESCENARIOS, SNAPSHOT, _sin_fecha

LINEA_BASE = json.loads(SNAPSHOT.read_text(encoding="utf-8"))


@pytest.mark.parametrize("nombre", list(ESCENARIOS))
def test_escenario_identico_a_linea_base(nombre):
    actual = _sin_fecha(ESCENARIOS[nombre]())
    assert actual == LINEA_BASE[nombre]


# --- Invariantes que un snapshot JSON no puede expresar ----------------------


def test_inventario_y_ventas_se_mutan_en_sitio(tmp_path):
    inventario, ventas = gestor.INVENTARIO, gestor.VENTAS
    gestor.agregarProducto("A1", "Café", 10.0, 10)
    gestor.registrar_venta("A1", 1)
    ruta = str(tmp_path / "d.json")
    almacen.guardar_datos(ruta)
    gestor.reiniciar_sistema()
    almacen.cargar_datos(ruta)
    assert gestor.INVENTARIO is inventario
    assert gestor.VENTAS is ventas


def test_busquedas_regresan_los_mismos_objetos_del_inventario():
    gestor.agregarProducto("A1", "Leche", 26.0, 3)
    assert gestor.buscarProducto("leche")[0] is gestor.INVENTARIO["A1"]
    assert reportes.productos_stock_bajo()[0] is gestor.INVENTARIO["A1"]


def test_tipos_de_retorno():
    assert gestor.agregarProducto("A1", "Café", 10.0, 10) is True
    assert gestor.agregarProducto("A1", "Café", 10.0, 10) is False
    assert isinstance(gestor.cotizar("A1", 2), float)
    assert gestor.cotizar("ZZ", 2) is None
    venta = gestor.registrar_venta("A1", 2)
    assert type(venta) is dict
    assert list(venta) == ["folio", "codigo", "nombre", "cantidad", "subtotal",
                           "descuento", "impuesto", "total", "cliente", "fecha",
                           "ticket"]
    assert list(gestor.INVENTARIO["A1"]) == ["codigo", "nombre", "precio", "stock"]
    top = reportes.mas_vendidos()
    assert type(top) is list and type(top[0]) is tuple


def test_venta_fallida_no_modifica_estado():
    gestor.agregarProducto("A1", "Café", 10.0, 2)
    antes = json.dumps(gestor.INVENTARIO)
    for args in [("A1", 3), ("A1", 0), ("ZZ", 1), ("", 1)]:
        assert gestor.registrar_venta(*args) is None
    assert json.dumps(gestor.INVENTARIO) == antes
    assert gestor.VENTAS == []
    assert gestor.registrar_venta("A1", 1)["folio"] == 1
