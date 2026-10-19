import pytest

from src.agent import gemini_agent

from src.agent.tools import (
    consultar_ventas_por_territorio,
    consultar_top_productos
)


def test_ejecutar_indicadores_generales(monkeypatch):

    datos_simulados = {
        "total_pedidos": 100,
        "ventas_productos": 5000
    }

    monkeypatch.setattr(
        gemini_agent,
        "consultar_indicadores_generales",
        lambda: datos_simulados
    )

    resultado = gemini_agent.ejecutar_herramienta(
        "consultar_indicadores_generales",
        {}
    )

    assert resultado == datos_simulados


def test_ejecutar_territorios(monkeypatch):

    def funcion_simulada(limite):
        return {"limite_recibido": limite}

    monkeypatch.setattr(
        gemini_agent,
        "consultar_ventas_por_territorio",
        funcion_simulada
    )

    resultado = gemini_agent.ejecutar_herramienta(
        "consultar_ventas_por_territorio",
        {"limite": 3}
    )

    assert resultado["limite_recibido"] == 3


def test_ejecutar_top_productos(monkeypatch):

    def funcion_simulada(limite, criterio):
        return {
            "limite": limite,
            "criterio": criterio
        }

    monkeypatch.setattr(
        gemini_agent,
        "consultar_top_productos",
        funcion_simulada
    )

    resultado = gemini_agent.ejecutar_herramienta(
        "consultar_top_productos",
        {"limite": 5, "criterio": "unidades"}
    )

    assert resultado["limite"] == 5
    assert resultado["criterio"] == "unidades"


def test_rechazar_herramienta_no_autorizada():

    with pytest.raises(ValueError):
        gemini_agent.ejecutar_herramienta(
            "eliminar_base_datos",
            {}
        )


def test_rechazar_argumentos_extra():

    with pytest.raises(ValueError):
        gemini_agent.ejecutar_herramienta(
            "consultar_indicadores_generales",
            {"limite": 10}
        )


def test_rechazar_limite_invalido_territorios():

    with pytest.raises(ValueError):
        consultar_ventas_por_territorio(
            limite=50
        )


def test_rechazar_limite_invalido_productos():

    with pytest.raises(ValueError):
        consultar_top_productos(
            limite=0,
            criterio="ingresos"
        )


def test_rechazar_criterio_invalido():

    with pytest.raises(ValueError):
        consultar_top_productos(
            limite=5,
            criterio="popularidad"
        )