import pandas as pd

def filtrar_datos_reporte(
    pedidos: pd.DataFrame,
    detalle: pd.DataFrame,
    anio: int | None = None,
    territorio: str | None = None
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Filtra pedidos y detalles por año y territorio.

    Conserva solamente los productos que pertenecen
    a los pedidos seleccionados.
    """

    # ======================================
    # 1. VALIDAR LOS PARAMETROS
    # ======================================

    if anio is not None:

        if (
            isinstance(anio, bool)
            or not isinstance(anio, int)
            or not 1900 <= anio <= 2100
        ):
            raise ValueError(
                "El año debe ser un entero entre "
                "1900 y 2100."
            )

    if territorio is not None:

        if (
            not isinstance(territorio, str)
            or not territorio.strip()
        ):
            raise ValueError(
                "El territorio debe ser un texto valido."
            )

    # ======================================
    # 2. VALIDAR COLUMNAS
    # ======================================

    columnas_pedidos = {
        "SalesOrderID",
        "OrderDate",
        "SubTotal",
        "Territorio"
    }

    columnas_detalle = {
        "SalesOrderID",
        "LineTotal"
    }

    if not columnas_pedidos.issubset(pedidos.columns):
        raise ValueError(
            "Faltan columnas requeridas en pedidos."
        )

    if not columnas_detalle.issubset(detalle.columns):
        raise ValueError(
            "Faltan columnas requeridas en detalle."
        )

    # Trabajar sobre copias independientes
    pedidos_filtrados = pedidos.copy()

    # ======================================
    # 3. FILTRAR POR AÑO
    # ======================================

    if anio is not None:

        fechas = pd.to_datetime(
            pedidos_filtrados["OrderDate"],
            errors="coerce"
        )

        if fechas.isna().any():
            raise ValueError(
                "Existen fechas de pedidos invalidas."
            )

        pedidos_filtrados = pedidos_filtrados.loc[
            fechas.dt.year == anio
        ].copy()

    # ======================================
    # 4. FILTRAR POR TERRITORIO
    # ======================================

    if territorio is not None:

        territorio_buscado = (
            territorio.strip().casefold()
        )

        nombres = (
            pedidos_filtrados["Territorio"]
            .astype("string")
            .str.strip()
            .str.casefold()
        )

        pedidos_filtrados = pedidos_filtrados.loc[
            nombres == territorio_buscado
        ].copy()

    # ======================================
    # 5. VALIDAR RESULTADOS
    # ======================================

    if pedidos_filtrados.empty:
        raise ValueError(
            "No se encontraron pedidos que "
            "coincidan con los filtros."
        )

    # ======================================
    # 6. FILTRAR EL DETALLE
    # ======================================

    ids_pedidos = pedidos_filtrados[
        "SalesOrderID"
    ]

    detalle_filtrado = detalle.loc[
        detalle["SalesOrderID"].isin(ids_pedidos)
    ].copy()

    if detalle_filtrado.empty:
        raise ValueError(
            "No se encontraron productos para "
            "los pedidos seleccionados."
        )

    # ======================================
    # 7. DEVOLVER RESULTADOS
    # ======================================

    return pedidos_filtrados, detalle_filtrado