import pytest

from src.agent import tools

@pytest.fixture
def reporte_simulado(monkeypatch, tmp_path):
    """Simula la extraccion y generacion del Excel."""

    pedidos = object()
    detalle = object()

    ruta = tmp_path / "reporte_prueba.xlsx"

    # Simular consultas SQL
    monkeypatch.setattr(
        tools,
        "obtener_pedidos",
        lambda: pedidos
    )

    monkeypatch.setattr(
        tools,
        "obtener_detalle_productos",
        lambda: detalle
    )

    # Simular creacion del archivo
    def crear_excel(**kwargs):

        assert set(kwargs) == {"pedidos", "detalle"}
        assert kwargs["pedidos"] is pedidos
        assert kwargs["detalle"] is detalle

        ruta.touch()
        return ruta

    monkeypatch.setattr(
        tools,
        "generar_reporte_excel",
        crear_excel
    )

    return ruta


def test_generar_reporte_con_conclusiones(
    monkeypatch,
    reporte_simulado
):
    """Verifica la integracion exitosa del reporte."""

    conclusiones = [
        "Conclusion de ventas.",
        "Conclusion de territorios.",
        "Conclusion de productos."
    ]

    llamadas = []

    # Simular respuesta de Gemini
    monkeypatch.setattr(
        tools,
        "generar_conclusiones_ia",
        lambda pedidos, detalle: conclusiones
    )

    # Simular incorporacion de conclusiones
    def agregar_conclusiones(ruta, textos):

        llamadas.append((ruta, textos))

    monkeypatch.setattr(
        tools,
        "agregar_conclusiones_ia",
        agregar_conclusiones
    )

    # Ejecutar la herramienta real
    resultado = tools.generar_reporte_ventas()

    assert resultado["estado"] == "generado"
    assert resultado["cantidad_hojas"] == 6
    assert resultado["cantidad_graficos"] == 2

    assert resultado["conclusiones_ia_en_excel"] is True

    assert "Conclusiones IA" in resultado["hojas"]

    assert len(llamadas) == 1
    assert llamadas[0][0] == reporte_simulado
    assert llamadas[0][1] == conclusiones


def test_reporte_si_falla_gemini(
    monkeypatch,
    reporte_simulado
):
    """Verifica que el Excel se conserve si falla Gemini."""

    def simular_error(pedidos, detalle):
        raise RuntimeError("Error simulado de Gemini")

    monkeypatch.setattr(
        tools,
        "generar_conclusiones_ia",
        simular_error
    )

    # La herramienta debe conservar el Excel
    resultado = tools.generar_reporte_ventas()

    assert resultado["estado"] == "generado"

    assert resultado["cantidad_hojas"] == 5

    assert resultado["conclusiones_ia_en_excel"] is False

    assert "advertencia" in resultado

    assert reporte_simulado.exists()