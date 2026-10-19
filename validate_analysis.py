from decimal import Decimal

from src.database.sales_queries import (
    obtener_pedidos,
    obtener_detalle_productos
)


def main():
    print("=== VALIDACION DE DATOS ===")

    pedidos = obtener_pedidos()
    detalles = obtener_detalle_productos()

    # Usar Decimal para mantener precision monetaria
    total_pedidos = sum(
        (Decimal(str(v)) for v in pedidos["SubTotal"]),
        Decimal("0")
    )

    total_detalles = sum(
        (Decimal(str(v)) for v in detalles["LineTotal"]),
        Decimal("0")
    )

    diferencia = abs(total_pedidos - total_detalles)

    pedidos_unicos = detalles["SalesOrderID"].nunique()

    print(f"Pedidos: {len(pedidos):,}")
    print(f"Lineas de pedido: {len(detalles):,}")
    print(f"Pedidos distintos en detalles: {pedidos_unicos:,}")
    print(f"Total cabeceras: {total_pedidos:,.2f}")
    print(f"Total detalles: {total_detalles:,.2f}")
    print(f"Diferencia absoluta: {diferencia:,.6f}")

    if pedidos_unicos != len(pedidos):
        raise AssertionError(
            "La cantidad de pedidos no coincide."
        )

    # Margen pequeño por diferencias de precision
    # entre SubTotal y LineTotal.
    if diferencia > Decimal("0.01"):
        raise AssertionError(
            "La diferencia entre totales es elevada."
        )

    print("\nValidacion completada correctamente.")


if __name__ == "__main__":
    main()