"""Casos límite descubiertos durante la refactorización.

Cada prueba fija el comportamiento ORIGINAL en un caso que ninguna otra suite
cubría y que una simplificación "obvia" habría cambiado sin que nadie lo notara.
La fase donde se descubrió va en el nombre de la clase.

Ejecutar desde la raíz del repositorio:
    pytest tests_caracterizacion -q
"""

import contextlib
import io

import pytest

import almacen
import gestor
import reportes

NAN = float("nan")


class TestR4Validacion:
    """`not cantidad > 0` no es lo mismo que `cantidad <= 0` cuando hay NaN."""

    def test_cantidad_nan_se_rechaza(self):
        gestor.agregarProducto("A1", "Café", 10.0, 5)
        assert gestor.registrar_venta("A1", NAN) is None
        assert gestor.ultimo_error == "cantidad invalida"
        assert gestor.INVENTARIO["A1"]["stock"] == 5
        assert gestor.VENTAS == []

    def test_stock_nan_se_rechaza_por_stock_insuficiente(self):
        gestor.agregarProducto("A1", "Raro", 10.0, NAN)
        assert gestor.registrar_venta("A1", 1) is None
        assert gestor.ultimo_error == "stock insuficiente"
        assert gestor.VENTAS == []


class TestR6Persistencia:
    """`except Exception` y el bucle del inventario se conservan a propósito."""

    def test_bytes_no_utf8_se_reportan_como_archivo_corrupto(self, tmp_path):
        ruta = tmp_path / "datos.json"
        ruta.write_bytes(b"\xff\xfe\x00{")
        assert almacen.cargar_datos(str(ruta)) is False
        assert gestor.ultimo_error == "archivo corrupto"

    def test_inventario_mal_formado_falla_en_lugar_de_cargar_basura(self, tmp_path):
        ruta = tmp_path / "datos.json"
        ruta.write_text('{"inventario": ["ab"], "ventas": []}', encoding="utf-8")
        with pytest.raises(TypeError):
            almacen.cargar_datos(str(ruta))
        assert "a" not in gestor.INVENTARIO


class TestR9Reportes:
    """Comprensiones y `sorted` sin cambiar tipos ni errores."""

    def test_cantidad_true_conserva_su_tipo_en_mas_vendidos(self):
        gestor.agregarProducto("A1", "Café", 10.0, 50)
        gestor.registrar_venta("A1", True)
        assert reportes.mas_vendidos() == [("A1", True)]
        assert type(reportes.mas_vendidos()[0][1]) is bool

    def test_buscar_none_con_inventario_vacio_regresa_lista_vacia(self):
        assert gestor.buscarProducto(None) == []

    def test_buscar_none_con_productos_falla(self):
        gestor.agregarProducto("A1", "Café", 10.0, 5)
        with pytest.raises(AttributeError):
            gestor.buscarProducto(None)

    def test_reporte_con_codigo_no_textual_falla_igual_que_antes(self):
        gestor.agregarProducto(5, "Codigo numerico", 10.0, 1)
        with contextlib.redirect_stdout(io.StringIO()), pytest.raises(TypeError):
            reportes.reporte_inventario()
