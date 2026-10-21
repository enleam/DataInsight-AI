import pandas as pd
import pytest

from app import dashboard


# ==========================================
# DATOS FICTICIOS PARA LAS PRUEBAS
# ==========================================

@pytest.fixture
def pedidos_ficticios():

    return pd.DataFrame({
        "SalesOrderID": [1, 2, 3],
        "OrderDate": [
            "2023-01-05",
            "2023-02-06",
            "2023-02-07"
        ],
        "SubTotal": [100, 200, 300],
        "Territorio": [
            "Norte",
            "Sur",
            "Norte"
        ]
    })


# ==========================================
# PRUEBA 1: INDICADORES GENERALES
# ==========================================

def test_indicadores_dashboard(
    monkeypatch,
    pedidos_ficticios
):

    monkeypatch.setattr(
        dashboard,
        "obtener_pedidos",
        lambda: pedidos_ficticios.copy()
    )

    datos = dashboard.cargar_datos_dashboard()

    kpis = datos["kpis"]

    assert kpis["total_pedidos"] == 3

    assert kpis["total_ventas"] == pytest.approx(600)

    assert kpis["ticket_promedio"] == pytest.approx(200)


# ==========================================
# PRUEBA 2: VENTAS MENSUALES
# ==========================================

def test_ventas_mensuales_dashboard(
    monkeypatch,
    pedidos_ficticios
):

    monkeypatch.setattr(
        dashboard,
        "obtener_pedidos",
        lambda: pedidos_ficticios.copy()
    )

    datos = dashboard.cargar_datos_dashboard()

    ventas = datos["ventas_mensuales"]

    assert len(ventas) == 2

    assert ventas.iloc[0]["Mes"].strftime(
        "%Y-%m"
    ) == "2023-01"

    assert ventas.iloc[0]["Ventas"] == pytest.approx(100)

    assert ventas.iloc[1]["Mes"].strftime(
        "%Y-%m"
    ) == "2023-02"

    assert ventas.iloc[1]["Ventas"] == pytest.approx(500)


# ==========================================
# PRUEBA 3: VENTAS POR TERRITORIO
# ==========================================

def test_territorios_dashboard(
    monkeypatch,
    pedidos_ficticios
):

    monkeypatch.setattr(
        dashboard,
        "obtener_pedidos",
        lambda: pedidos_ficticios.copy()
    )

    datos = dashboard.cargar_datos_dashboard()

    territorios = (
        datos["territorios"]
        .set_index("Territorio")
    )

    assert territorios.loc[
        "Norte", "Ventas"
    ] == pytest.approx(400)

    assert territorios.loc[
        "Sur", "Ventas"
    ] == pytest.approx(200)

    assert territorios.loc[
        "Norte", "Pedidos"
    ] == 2

    assert territorios.loc[
        "Sur", "Pedidos"
    ] == 1


# ==========================================
# PRUEBA 4: BASE DE DATOS SIN PEDIDOS
# ==========================================

def test_dashboard_sin_pedidos(monkeypatch):

    monkeypatch.setattr(
        dashboard,
        "obtener_pedidos",
        lambda: pd.DataFrame()
    )

    with pytest.raises(
        ValueError,
        match="No se encontraron pedidos"
    ):

        dashboard.cargar_datos_dashboard()