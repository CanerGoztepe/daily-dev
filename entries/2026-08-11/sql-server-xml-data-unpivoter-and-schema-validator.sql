-- Sample structure: <Payload><Item id='101'><Name>Widget</Name><Price>19.99</Price></Item></Payload>
DECLARE @XmlData XML = '<Payload><Item id="101"><Name>Widget</Name><Price>19.99</Price></Item><Item id="102"><Name>Gadget</Name><Price>25.50</Price></Item></Payload>';

-- The query extracts nodes, shreds into a table, and performs explicit data type validation
SELECT 
    T.c.value('@id', 'INT') AS ItemID,
    T.c.value('(Name)[1]', 'NVARCHAR(100)') AS ItemName,
    TRY_CAST(T.c.value('(Price)[1]', 'VARCHAR(20)') AS DECIMAL(18,2)) AS Price
FROM @XmlData.nodes('/Payload/Item') AS T(c)
WHERE T.c.value('@id', 'INT') IS NOT NULL;

-- Example of validating structure/completeness
-- This helps identify incomplete XML nodes that failed to parse correctly
SELECT 
    T.c.query('.') AS RawNode,
    'Missing Name' AS Error
FROM @XmlData.nodes('/Payload/Item') AS T(c)
WHERE T.c.exist('Name') = 0;

/* 
Assumptions:
1. The XML structure is consistent with the provided schema path.
2. TRY_CAST is used to safely handle non-numeric data in fields intended for decimals.
3. The use of [1] index is standard for scalar node extraction in SQL Server XML shredding.
*/
