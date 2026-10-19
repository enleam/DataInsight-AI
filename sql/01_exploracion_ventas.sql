USE AdventureWorks2022;
GO

-- 1. Resumen general de pedidos
SELECT
    COUNT(*) AS TotalPedidos,
    MIN(OrderDate) AS PrimeraFecha,
    MAX(OrderDate) AS UltimaFecha,
    SUM(SubTotal) AS TotalVentasProductos
FROM Sales.SalesOrderHeader;

-- 2. Pedidos y ventas por año
SELECT
    YEAR(OrderDate) AS Anio,
    COUNT(*) AS CantidadPedidos,
    SUM(SubTotal) AS VentasProductos
FROM Sales.SalesOrderHeader
GROUP BY YEAR(OrderDate)
ORDER BY Anio;

-- 3. Ventas por territorio
SELECT
    COALESCE(st.Name, 'Sin territorio') AS Territorio,
    COUNT(*) AS CantidadPedidos,
    SUM(soh.SubTotal) AS VentasProductos
FROM Sales.SalesOrderHeader AS soh
LEFT JOIN Sales.SalesTerritory AS st
    ON soh.TerritoryID = st.TerritoryID
GROUP BY st.Name
ORDER BY VentasProductos DESC;