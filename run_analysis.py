
from src.database.sales_queries import (
    obtener_pedidos,
    obtener_detalle_productos
)

from src.analytics.sales_analysis import (
    preparar_pedidos,
    calcular_kpis,
    ventas_por_anio,
    ventas_por_mes,
    ventas_por_territorio,
    analizar_productos
)


def main():

    print("=== DATAINSIGHT AI ===")
    print("Sprint 2 - Analisis de ventas\n")

    # 1. Extraer pedidos
    print("Extrayendo datos de SQL Server...")
    df = obtener_pedidos()

    print(f"Registros extraidos: {len(df):,}")

    # 2. Preparar los datos
    df = preparar_pedidos(df)

    # 3. Calcular indicadores generales
    kpis = calcular_kpis(df)

    print("\n=== INDICADORES GENERALES ===")

    print(f"Total de pedidos: {kpis['total_pedidos']:,}")
    print(f"Ventas de productos: {kpis['total_ventas']:,.2f}")
    print(f"Ticket promedio: {kpis['ticket_promedio']:,.2f}")
    print(f"Primera fecha: {kpis['primera_fecha'].date()}")
    print(f"Ultima fecha: {kpis['ultima_fecha'].date()}")

    # 4. Analisis de ventas anuales
    resumen_anual = ventas_por_anio(df)

    print("\n=== VENTAS POR ANIO ===")
    print(
        resumen_anual.to_string(
            index=False,
            float_format=lambda x: f"{x:,.2f}"
        )
    )

    # 5. Analisis de ventas mensuales
    resumen_mensual = ventas_por_mes(df)

    print("\n=== VENTAS MENSUALES ===")
    print(
        resumen_mensual.head(12).to_string(
            index=False,
            float_format=lambda x: f"{x:,.2f}"
        )
    )

    # 6. Analisis de ventas por territorio
    resumen_territorios = ventas_por_territorio(df)

    print("\n=== VENTAS POR TERRITORIO ===")
    print(
        resumen_territorios.to_string(
            index=False,
            float_format=lambda x: f"{x:,.2f}"
        )
    )

    # 7. Extraer detalle de productos
    print("\nExtrayendo detalle de productos...")

    detalle_productos = obtener_detalle_productos()

    print(
        f"Lineas de pedido extraidas: "
        f"{len(detalle_productos):,}"
    )

    # 8. Analizar productos
    resumen_productos = analizar_productos(
        detalle_productos
    )

    # 9. Ranking por ingresos
    print("\n=== TOP 10 PRODUCTOS POR INGRESOS ===")

    print(
        resumen_productos.head(10).to_string(
            index=False,
            float_format=lambda x: f"{x:,.2f}"
        )
    )

    # 10. Ranking por unidades vendidas
    top_unidades = (
        resumen_productos.sort_values(
            ["UnidadesVendidas", "ProductID"],
            ascending=[False, True]
        )
        .head(10)
    )

    print("\n=== TOP 10 PRODUCTOS POR UNIDADES ===")

    print(
        top_unidades.to_string(
            index=False,
            float_format=lambda x: f"{x:,.2f}"
        )
    )


if __name__ == "__main__":
    main()