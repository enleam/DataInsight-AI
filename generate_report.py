from src.database.sales_queries import (
    obtener_pedidos,
    obtener_detalle_productos
)

from src.reports.excel_generator import (
    generar_reporte_excel
)


def main():

    print("=== DATAINSIGHT AI ===")
    print("Sprint 4 - Generacion de reportes Excel\n")

    # 1. Extraer datos desde SQL Server
    print("Consultando AdventureWorks2022...")

    pedidos = obtener_pedidos()
    detalle = obtener_detalle_productos()

    print(f"Pedidos extraidos: {len(pedidos):,}")
    print(f"Lineas de detalle: {len(detalle):,}")

    # 2. Generar el Excel
    print("\nGenerando reporte empresarial...")

    ruta = generar_reporte_excel(
        pedidos=pedidos,
        detalle=detalle
    )

    print("\n=== REPORTE GENERADO ===")
    print(f"Archivo: {ruta}")
    print("Generacion completada correctamente.")


if __name__ == "__main__":
    main()