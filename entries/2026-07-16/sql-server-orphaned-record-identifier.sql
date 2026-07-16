-- Assumes Tables: 
-- Orders (OrderID INT PRIMARY KEY, OrderDate DATETIME)
-- OrderDetails (DetailID INT PRIMARY KEY, OrderID INT)

SET NOCOUNT ON;

DECLARE @OrphanReport TABLE (
    OrderID INT,
    DetectionDate DATETIME DEFAULT GETDATE()
);

INSERT INTO @OrphanReport (OrderID)
SELECT 
    o.OrderID
FROM Orders o
LEFT JOIN OrderDetails od ON o.OrderID = od.OrderID
WHERE od.OrderID IS NULL
  AND o.OrderDate >= DATEADD(MONTH, -6, GETDATE());

-- Return the report of orphans
SELECT 
    OrderID,
    DetectionDate,
    'Orphan detected: No associated details found for order in last 6 months' AS IssueDescription
FROM @OrphanReport
ORDER BY OrderID DESC;

-- Validation: Ensure we found records to report
IF EXISTS (SELECT 1 FROM @OrphanReport)
BEGIN
    PRINT 'Audit Complete: Orphaned records identified.';
END
ELSE
BEGIN
    PRINT 'Audit Complete: No orphaned records found.';
END
