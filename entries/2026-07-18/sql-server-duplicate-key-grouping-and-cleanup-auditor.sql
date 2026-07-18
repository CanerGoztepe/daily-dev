/* 
Assumption: TargetTable has columns: ID (PK), BusinessKey, CreatedAt, and DataValue.
This script identifies duplicates based on BusinessKey, keeping the record with the latest CreatedAt.
*/

WITH RankedRecords AS (
    SELECT 
        ID,
        BusinessKey,
        CreatedAt,
        ROW_NUMBER() OVER (
            PARTITION BY BusinessKey 
            ORDER BY CreatedAt DESC
        ) as RowRank
    FROM TargetTable
),
DuplicateReport AS (
    SELECT 
        ID,
        BusinessKey,
        CreatedAt,
        CASE WHEN RowRank = 1 THEN 'KEEP' ELSE 'DELETE' END as ActionRequired
    FROM RankedRecords
    WHERE BusinessKey IN (
        SELECT BusinessKey 
        FROM TargetTable 
        GROUP BY BusinessKey 
        HAVING COUNT(*) > 1
    )
)
SELECT 
    ID,
    BusinessKey,
    CreatedAt,
    ActionRequired,
    'DELETE FROM TargetTable WHERE ID = ' + CAST(ID AS VARCHAR(20)) + ';' as CleanupScript
FROM DuplicateReport
WHERE ActionRequired = 'DELETE'
ORDER BY BusinessKey, CreatedAt DESC;
