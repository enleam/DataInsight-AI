import json

from google.genai import types

from src.agent.gemini_client import (
    crear_cliente_gemini,
    obtener_modelo
)

from src.analytics.sales_analysis import (
    preparar_pedidos,
    calcular_kpis,
    ventas_por_territorio,
    analizar_productos
)


def generar_conclusiones_ia(pedidos, detalle) -> list[str]:
    """Genera tres conclusiones a partir de KPIs reales."""

    # 1. Calcular resultados con Pandas
    pedidos = preparar_pedidos(pedidos)

    kpis = calcular_kpis(pedidos)
    territorios = ventas_por_territorio(pedidos)
    productos = analizar_productos(detalle)

    lider_territorio = territorios.iloc[0]
    lider_ingresos = productos.iloc[0]

    lider_unidades = (
        productos.sort_values(
            "UnidadesVendidas",
            ascending=False
        ).iloc[0]
    )

    # 2. Preparar datos resumidos para Gemini
    datos = {
        "fecha_inicio": str(kpis["primera_fecha"].date()),
        "fecha_fin": str(kpis["ultima_fecha"].date()),
        "total_pedidos": int(kpis["total_pedidos"]),
        "ventas_productos": round(
            float(kpis["total_ventas"]), 2
        ),
        "ticket_promedio": round(
            float(kpis["ticket_promedio"]), 2
        ),
        "territorio_lider": {
            "nombre": str(lider_territorio["Territorio"]),
            "ventas": round(
                float(lider_territorio["VentasProductos"]), 2
            )
        },
        "producto_lider_ingresos": {
            "nombre": str(lider_ingresos["NombreProducto"]),
            "ventas": round(
                float(lider_ingresos["VentasProductos"]), 2
            )
        },
        "producto_lider_unidades": {
            "nombre": str(lider_unidades["NombreProducto"]),
            "unidades": int(
                lider_unidades["UnidadesVendidas"]
            )
        }
    }

    instrucciones = """
    Actua como analista de datos empresarial.

    Genera exactamente tres conclusiones en español,
    breves y profesionales, utilizando exclusivamente
    los indicadores proporcionados.

    Reglas:
    - No inventes cifras, monedas ni porcentajes.
    - No afirmes causalidad sin evidencia.
    - No afirmes rentabilidad o fidelidad de clientes.
    - No confundas ingresos con unidades vendidas.
    - Distingue ventas acumuladas de ventas anuales.
    - No compares años parciales como si fueran completos.
    - No hagas recomendaciones sin evidencia suficiente.
    - Cada conclusion debe tener una o dos oraciones.
    """

    # 3. Solicitar conclusiones estructuradas
    with crear_cliente_gemini() as cliente:

        respuesta = cliente.models.generate_content(
            model=obtener_modelo(),
            contents=(
                instrucciones
                + "\n\nIndicadores verificados:\n"
                + json.dumps(datos, ensure_ascii=False)
            ),
            config=types.GenerateContentConfig(
                temperature=0.2,
                response_mime_type="application/json",
                response_json_schema={
                    "type": "object",
                    "properties": {
                        "conclusiones": {
                            "type": "array",
                            "items": {"type": "string"},
                            "minItems": 3,
                            "maxItems": 3
                        }
                    },
                    "required": ["conclusiones"]
                }
            )
        )

    if not respuesta.text:
        raise RuntimeError(
            "Gemini no devolvio conclusiones."
        )

    # 4. Validar la estructura recibida
    contenido = json.loads(respuesta.text)
    conclusiones = contenido.get("conclusiones")

    if (
        not isinstance(conclusiones, list)
        or len(conclusiones) != 3
        or any(
            not isinstance(item, str) or not item.strip()
            for item in conclusiones
        )
    ):
        raise ValueError(
            "Las conclusiones de Gemini no son validas."
        )

    return [
        conclusion.strip()
        for conclusion in conclusiones
    ]