-- Assumes a table 'Categories' exists: (ID INT, ParentID INT, Name NVARCHAR(100))
WITH HierarchyCTE AS (
    -- Anchor member: root nodes
    SELECT 
        ID, 
        Name, 
        CAST(Name AS NVARCHAR(MAX)) AS HierarchyPath, 
        0 AS Depth
    FROM Categories
    WHERE ParentID IS NULL
    
    UNION ALL
    
    -- Recursive member: child nodes
    SELECT 
        c.ID, 
        c.Name, 
        CAST(h.HierarchyPath + ' > ' + c.Name AS NVARCHAR(MAX)), 
        h.Depth + 1
    FROM Categories c
    INNER JOIN HierarchyCTE h ON c.ParentID = h.ID
)
SELECT 
    ID, 
    Name, 
    HierarchyPath, 
    Depth, 
    -- Indent based on depth for visual representation in reports
    REPLICATE('  ', Depth) + Name AS VisualTree
FROM HierarchyCTE
ORDER BY HierarchyPath;
