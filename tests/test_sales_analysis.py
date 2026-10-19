import pandas as pd
import pytest

from src.analytics.sales_analysis import (
    preparar_pedidos,
    calcular_kpis,
    ventas_por_mes,
    ventas_por_territorio,
    analizar_productos
)


@pytest.fixture
def pedidos():
    """Datos ficticios para probar el motor analitico."""

    df = pd.DataFrame({
        "SalesOrderID": [1, 2, 3],
        "OrderDate": [
            "2023-01-05",
            "2023-01-15",
            "2023-02-10"
        ],
        "SubTotal": [100, 200, 300],
        "Territorio": ["Norte", "Sur", "Norte"]
    })

    return preparar_pedidos(df)


def test_calcular_kpis(pedidos):
    kpis = calcular_kpis(pedidos)

    assert kpis["total_pedidos"] == 3
    assert kpis["total_ventas"] == pytest.approx(600)
    assert kpis["ticket_promedio"] == pytest.approx(200)


def test_ventas_por_mes(pedidos):
    resultado = ventas_por_mes(pedidos)

    assert len(resultado) == 2
    assert resultado.iloc[0]["Mes"] == "2023-01"
    assert resultado.iloc[0]["CantidadPedidos"] == 2
    assert resultado.iloc[0]["VentasProductos"] == pytest.approx(300)


def test_ventas_por_territorio(pedidos):
    resultado = ventas_por_territorio(pedidos)

    assert resultado.iloc[0]["Territorio"] == "Norte"
    assert resultado.iloc[0]["VentasProductos"] == pytest.approx(400)


def test_analizar_productos():
    detalle = pd.DataFrame({
        "SalesOrderID": [1, 1, 2],
        "ProductID": [10, 20, 10],
        "NombreProducto": ["Producto A", "Producto B", "Producto A"],
        "OrderQty": [2, 1, 3],
        "LineTotal": [100, 50, 150]
    })

    resultado = analizar_productos(detalle)

    producto_a = resultado.iloc[0]

    assert producto_a["ProductID"] == 10
    assert producto_a["UnidadesVendidas"] == 5
    assert producto_a["CantidadPedidos"] == 2
    assert producto_a["VentasProductos"] == pytest.approx(250)