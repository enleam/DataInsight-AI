import pandas as pd
import pytest

from src.reports.report_filters import (
    filtrar_datos_reporte
)


@pytest.fixture
def datos_ficticios():

    pedidos = pd.DataFrame({
        "SalesOrderID": [101, 102, 103, 104],
        "OrderDate": [
            "2012-01-10",
            "2013-02-15",
            "2013-06-20",
            "2014-03-10"
        ],
        "SubTotal": [100, 200, 300, 400],
        "Territorio": [
            "Southwest",
            "Southwest",
            "Canada",
            "Canada"
        ]
    })

    detalle = pd.DataFrame({
        "SalesOrderID": [
            101, 101, 102, 103, 103, 104
        ],
        "ProductID": [
            1, 2, 3, 4, 5, 6
        ],
        "NombreProducto": [
            "Producto A",
            "Producto B",
            "Producto C",
            "Producto D",
            "Producto E",
            "Producto F"
        ],
        "OrderQty": [1, 1, 1, 1, 1, 1],
        "LineTotal": [
            60, 40, 200, 120, 180, 400
        ]
    })

    return pedidos, detalle


# PRUEBA 1: SIN FILTROS

def test_reporte_sin_filtros(datos_ficticios):

    pedidos, detalle = datos_ficticios

    p, d = filtrar_datos_reporte(
        pedidos,
        detalle
    )

    assert len(p) == 4
    assert len(d) == 6


# PRUEBA 2: FILTRO POR AÑO

def test_reporte_por_anio(datos_ficticios):

    pedidos, detalle = datos_ficticios

    p, d = filtrar_datos_reporte(
        pedidos,
        detalle,
        anio=2013
    )

    assert set(p["SalesOrderID"]) == {
        102, 103
    }

    assert set(d["SalesOrderID"]) == {
        102, 103
    }

    assert p["SubTotal"].sum() == 500
    assert d["LineTotal"].sum() == 500


# PRUEBA 3: FILTRO POR TERRITORIO

def test_reporte_por_territorio(datos_ficticios):

    pedidos, detalle = datos_ficticios

    p, d = filtrar_datos_reporte(
        pedidos,
        detalle,
        territorio="canada"
    )

    assert set(p["SalesOrderID"]) == {
        103, 104
    }

    assert set(d["SalesOrderID"]) == {
        103, 104
    }

    assert p["SubTotal"].sum() == 700


# PRUEBA 4: DOS FILTROS SIMULTANEOS

def test_reporte_anio_y_territorio(
    datos_ficticios
):

    pedidos, detalle = datos_ficticios

    p, d = filtrar_datos_reporte(
        pedidos,
        detalle,
        anio=2013,
        territorio="Canada"
    )

    assert list(p["SalesOrderID"]) == [103]

    assert set(d["SalesOrderID"]) == {103}

    assert len(d) == 2

    assert p["SubTotal"].sum() == 300
    assert d["LineTotal"].sum() == 300


# PRUEBA 5: FILTRO SIN RESULTADOS

def test_reporte_sin_resultados(datos_ficticios):

    pedidos, detalle = datos_ficticios

    with pytest.raises(
        ValueError,
        match="No se encontraron pedidos"
    ):

        filtrar_datos_reporte(
            pedidos,
            detalle,
            anio=2020
        )


# PRUEBA 6: PARAMETROS INVALIDOS

def test_rechazar_filtros_invalidos(
    datos_ficticios
):

    pedidos, detalle = datos_ficticios

    with pytest.raises(ValueError):
        filtrar_datos_reporte(
            pedidos,
            detalle,
            anio="2013"
        )

    with pytest.raises(ValueError):
        filtrar_datos_reporte(
            pedidos,
            detalle,
            anio=True
        )

    with pytest.raises(ValueError):
        filtrar_datos_reporte(
            pedidos,
            detalle,
            territorio=" "
        )