from src.database.sales_queries import (
    obtener_pedidos,
    obtener_detalle_productos
)

from src.analytics.sales_analysis import (
    preparar_pedidos,
    calcular_kpis,
    ventas_por_territorio,
    analizar_productos
)


def consultar_indicadores_generales() -> dict:
    """Obtiene los KPIs generales de ventas."""

    df = preparar_pedidos(obtener_pedidos())

    if df.empty:
        return {"mensaje": "No existen pedidos."}

    kpis = calcular_kpis(df)

    return {
        "total_pedidos": int(kpis["total_pedidos"]),
        "ventas_productos": round(
            float(kpis["total_ventas"]), 2
        ),
        "ticket_promedio": round(
            float(kpis["ticket_promedio"]), 2
        ),
        "primera_fecha": str(
            kpis["primera_fecha"].date()
        ),
        "ultima_fecha": str(
            kpis["ultima_fecha"].date()
        ),
        "metrica": "SubTotal",
        "moneda": "no especificada"
    }


def consultar_ventas_por_territorio(limite: int) -> dict:
    """Obtiene los territorios con mayores ingresos."""

    if type(limite) is not int or not 1 <= limite <= 10:
        raise ValueError(
            "El limite debe ser un entero entre 1 y 10."
        )

    df = preparar_pedidos(obtener_pedidos())

    if df.empty:
        return {"territorios": [], "mensaje": "Sin datos"}

    resumen = ventas_por_territorio(df)
    top = resumen.head(limite)

    resultados = []

    for _, fila in top.iterrows():
        resultados.append({
            "territorio": str(fila["Territorio"]),
            "cantidad_pedidos": int(
                fila["CantidadPedidos"]
            ),
            "ventas_productos": round(
                float(fila["VentasProductos"]), 2
            )
        })

    return {
        "metrica": "SubTotal",
        "moneda": "no especificada",
        "periodo_inicio": str(
            df["OrderDate"].min().date()
        ),
        "periodo_fin": str(
            df["OrderDate"].max().date()
        ),
        "territorios": resultados
    }


def consultar_top_productos(
    limite: int,
    criterio: str
) -> dict:
    """Obtiene los productos lideres por ingresos o unidades."""

    if type(limite) is not int or not 1 <= limite <= 10:
        raise ValueError(
            "El limite debe ser un entero entre 1 y 10."
        )

    if criterio not in ("ingresos", "unidades"):
        raise ValueError(
            "El criterio debe ser ingresos o unidades."
        )

    detalle = obtener_detalle_productos()
    resumen = analizar_productos(detalle)

    columna = (
        "VentasProductos"
        if criterio == "ingresos"
        else "UnidadesVendidas"
    )

    top = (
        resumen.sort_values(
            [columna, "ProductID"],
            ascending=[False, True]
        )
        .head(limite)
    )

    productos = []

    for _, fila in top.iterrows():
        productos.append({
            "producto_id": int(fila["ProductID"]),
            "nombre": str(fila["NombreProducto"]),
            "unidades_vendidas": int(
                fila["UnidadesVendidas"]
            ),
            "cantidad_pedidos": int(
                fila["CantidadPedidos"]
            ),
            "ventas_productos": round(
                float(fila["VentasProductos"]), 2
            )
        })

    return {
        "criterio_ordenacion": criterio,
        "metrica_ingresos": "LineTotal",
        "moneda": "no especificada",
        "productos": productos
    }