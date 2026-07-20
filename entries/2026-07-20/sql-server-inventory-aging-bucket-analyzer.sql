-- Sample Table Assumption:
-- CREATE TABLE InventoryMovements (ItemID INT, Quantity INT, LastMovementDate DATETIME);

WITH AgingCalculation AS (
    SELECT 
        ItemID,
        Quantity,
        DATEDIFF(DAY, LastMovementDate, GETDATE()) AS DaysSinceLastMove
    FROM InventoryMovements
    WHERE LastMovementDate IS NOT NULL
),
AgingBuckets AS (
    SELECT 
        ItemID,
        Quantity,
        CASE 
            WHEN DaysSinceLastMove <= 30 THEN '0-30 Days (Active)'
            WHEN DaysSinceLastMove <= 90 THEN '31-90 Days (Normal)'
            WHEN DaysSinceLastMove <= 180 THEN '91-180 Days (Slow)'
            ELSE '180+ Days (Obsolete)'
        END AS AgingCategory,
        CASE 
            WHEN DaysSinceLastMove <= 30 THEN 1
            WHEN DaysSinceLastMove <= 90 THEN 2
            WHEN DaysSinceLastMove <= 180 THEN 3
            ELSE 4
        END AS SortOrder
    FROM AgingCalculation
)
SELECT 
    AgingCategory,
    SUM(Quantity) AS TotalQuantity,
    COUNT(ItemID) AS UniqueItemCount,
    FORMAT(SUM(Quantity) * 100.0 / NULLIF(SUM(SUM(Quantity)) OVER(), 0), 'N2') + '%' AS PercentageOfTotalStock
FROM AgingBuckets
GROUP BY AgingCategory, SortOrder
ORDER BY SortOrder;
