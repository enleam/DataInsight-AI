import pandas as pd

def preparar_pedidos(df: pd.DataFrame) -> pd.DataFrame:
    """Valida y prepara los datos de ventas."""

    datos = df.copy()

    # Convertir la fecha a formato datetime
    datos["OrderDate"] = pd.to_datetime(
        datos["OrderDate"],
        errors="raise"
    )

    # Convertir las ventas a formato numérico
    datos["SubTotal"] = pd.to_numeric(
        datos["SubTotal"],
        errors="raise"
    )

    # Validar campos obligatorios
    columnas_obligatorias = [
        "SalesOrderID",
        "OrderDate",
        "SubTotal"
    ]

    if datos[columnas_obligatorias].isna().any().any():
        raise ValueError(
            "Existen valores nulos en campos obligatorios."
        )

    # Evitar pedidos duplicados
    if datos["SalesOrderID"].duplicated().any():
        raise ValueError(
            "Existen identificadores de pedido duplicados."
        )

    return datos

def calcular_kpis(df: pd.DataFrame) -> dict:
    """Calcula indicadores generales de ventas."""

    total_pedidos = df["SalesOrderID"].nunique()
    total_ventas = df["SubTotal"].sum()

    ticket_promedio = (
        total_ventas / total_pedidos
        if total_pedidos > 0
        else 0
    )

    return {
        "total_pedidos": total_pedidos,
        "total_ventas": total_ventas,
        "ticket_promedio": ticket_promedio,
        "primera_fecha": df["OrderDate"].min(),
        "ultima_fecha": df["OrderDate"].max()
    }

def ventas_por_anio(df: pd.DataFrame) -> pd.DataFrame:
    """Agrupa las ventas y pedidos por año."""

    datos = df.copy()

    datos["Anio"] = datos["OrderDate"].dt.year

    resumen = (
        datos.groupby("Anio", as_index=False)
        .agg(
            CantidadPedidos=("SalesOrderID", "nunique"),
            VentasProductos=("SubTotal", "sum")
        )
        .sort_values("Anio")
    )

    return resumen

def ventas_por_mes(df: pd.DataFrame) -> pd.DataFrame:
    """Calcula las ventas y pedidos por mes."""

    datos = df.copy()

    datos["Mes"] = (
        datos["OrderDate"]
        .dt.to_period("M")
        .astype(str)
    )

    resumen = (
        datos.groupby("Mes", as_index=False)
        .agg(
            CantidadPedidos=("SalesOrderID", "nunique"),
            VentasProductos=("SubTotal", "sum")
        )
        .sort_values("Mes")
    )

    return resumen

def ventas_por_territorio(
    df: pd.DataFrame
) -> pd.DataFrame:
    """Analiza el rendimiento por territorio."""

    datos = df.copy()

    datos["Territorio"] = (
        datos["Territorio"].fillna("Sin territorio")
    )

    resumen = (
        datos.groupby("Territorio", as_index=False)
        .agg(
            CantidadPedidos=("SalesOrderID", "nunique"),
            VentasProductos=("SubTotal", "sum")
        )
        .sort_values(
            "VentasProductos",
            ascending=False
        )
    )

    return resumen

def analizar_productos(df: pd.DataFrame) -> pd.DataFrame:
    """Calcula ventas, unidades y pedidos por producto."""

    datos = df.copy()

    if datos.empty:
        raise ValueError(
            "No se encontraron detalles de productos."
        )

    # Convertir columnas a formato numerico
    datos["OrderQty"] = pd.to_numeric(
        datos["OrderQty"],
        errors="raise"
    )

    datos["LineTotal"] = pd.to_numeric(
        datos["LineTotal"],
        errors="raise"
    ).astype("float64")

    # Validar campos obligatorios
    columnas = [
        "SalesOrderID",
        "ProductID",
        "NombreProducto",
        "OrderQty",
        "LineTotal"
    ]

    if datos[columnas].isna().any().any():
        raise ValueError(
            "Existen valores nulos en el detalle de productos."
        )

    # Agrupar por identificador y nombre de producto
    resumen = (
        datos.groupby(
            ["ProductID", "NombreProducto"],
            as_index=False
        )
        .agg(
            UnidadesVendidas=("OrderQty", "sum"),
            CantidadPedidos=("SalesOrderID", "nunique"),
            VentasProductos=("LineTotal", "sum")
        )
        .sort_values(
            ["VentasProductos", "ProductID"],
            ascending=[False, True]
        )
    )

    return resumen