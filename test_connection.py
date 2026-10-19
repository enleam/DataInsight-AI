from contextlib import closing

from src.database.connection import get_connection


def main():
    consulta = """
        SELECT
            DB_NAME() AS BaseDeDatos,
            COUNT(*) AS CantidadPedidos
        FROM Sales.SalesOrderHeader;
    """

    with closing(get_connection()) as conexion:
        cursor = conexion.cursor()
        cursor.execute(consulta)

        resultado = cursor.fetchone()

        print("Conexion exitosa con SQL Server")
        print("Base de datos:", resultado.BaseDeDatos)
        print("Cantidad de pedidos:", resultado.CantidadPedidos)


if __name__ == "__main__":
    main()