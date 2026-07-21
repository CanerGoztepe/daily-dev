-- Assumptions: 
-- 1. Table [dbo].[SchemaBaseline] exists with columns: TableName, ColumnName, DataType, MaxLength, IsNullable
-- 2. This script compares system catalog views against this baseline to detect schema drift.

SELECT 
    t.name AS TableName,
    c.name AS ColumnName,
    st.name AS CurrentDataType,
    c.max_length AS CurrentMaxLength,
    c.is_nullable AS CurrentIsNullable,
    'DRIFT DETECTED' AS Status
FROM sys.columns c
JOIN sys.tables t ON c.object_id = t.object_id
JOIN sys.types st ON c.user_type_id = st.user_type_id
LEFT JOIN [dbo].[SchemaBaseline] b 
    ON t.name = b.TableName 
    AND c.name = b.ColumnName
WHERE b.TableName IS NOT NULL
AND (
    st.name <> b.DataType
    OR c.max_length <> b.MaxLength
    OR c.is_nullable <> b.IsNullable
)
UNION ALL
SELECT 
    b.TableName,
    b.ColumnName,
    b.DataType,
    b.MaxLength,
    b.IsNullable,
    'MISSING COLUMN' AS Status
FROM [dbo].[SchemaBaseline] b
LEFT JOIN sys.columns c 
    ON b.ColumnName = c.name 
    AND OBJECT_ID(b.TableName) = c.object_id
WHERE c.name IS NULL
UNION ALL
SELECT 
    t.name,
    c.name,
    st.name,
    c.max_length,
    c.is_nullable,
    'UNTRACKED COLUMN' AS Status
FROM sys.columns c
JOIN sys.tables t ON c.object_id = t.object_id
JOIN sys.types st ON c.user_type_id = st.user_type_id
LEFT JOIN [dbo].[SchemaBaseline] b 
    ON t.name = b.TableName 
    AND c.name = b.ColumnName
WHERE b.TableName IS NULL
AND t.name IN (SELECT DISTINCT TableName FROM [dbo].[SchemaBaseline]);
