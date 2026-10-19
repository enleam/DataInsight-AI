from contextlib import closing

import pandas as pd

from src.database.connection import get_connection


def obtener_pedidos() -> pd.DataFrame:
    """Extrae los pedidos de AdventureWorks2022."""

    query = """
        SELECT
            soh.SalesOrderID,
            soh.OrderDate,
            soh.SubTotal,
            soh.TerritoryID,
            st.Name AS Territorio
        FROM Sales.SalesOrderHeader AS soh
        LEFT JOIN Sales.SalesTerritory AS st
            ON soh.TerritoryID = st.TerritoryID
        ORDER BY soh.SalesOrderID;
    """

    with closing(get_connection()) as conexion:
        with closing(conexion.cursor()) as cursor:
            cursor.execute(query)

            columnas = [
                columna[0]
                for columna in cursor.description
            ]

            filas = [
                tuple(fila)
                for fila in cursor.fetchall()
            ]

    df = pd.DataFrame(filas, columns=columnas)

    return df

def obtener_detalle_productos() -> pd.DataFrame:
    """Extrae el detalle de productos vendidos."""

    query = """
        SELECT
            sod.SalesOrderID,
            sod.ProductID,
            p.Name AS NombreProducto,
            sod.OrderQty,
            sod.LineTotal
        FROM Sales.SalesOrderDetail AS sod
        INNER JOIN Production.Product AS p
            ON sod.ProductID = p.ProductID
        ORDER BY sod.SalesOrderID;
    """

    with closing(get_connection()) as conexion:
        with closing(conexion.cursor()) as cursor:
            cursor.execute(query)

            columnas = [
                columna[0]
                for columna in cursor.description
            ]

            filas = [
                tuple(fila)
                for fila in cursor.fetchall()
            ]

    return pd.DataFrame(filas, columns=columnas)