-- Table Assumptions:
-- ProductionData (ID INT PRIMARY KEY, DataVal NVARCHAR(100), LastModified DATETIME)
-- StagingData (ID INT PRIMARY KEY, DataVal NVARCHAR(100), LastModified DATETIME)

WITH ProductionHash AS (
    SELECT 
        ID, 
        HASHBYTES('SHA2_256', CONCAT(ID, '|', DataVal, '|', LastModified)) AS RowHash
    FROM ProductionData
),
StagingHash AS (
    SELECT 
        ID, 
        HASHBYTES('SHA2_256', CONCAT(ID, '|', DataVal, '|', LastModified)) AS RowHash
    FROM StagingData
)
SELECT 
    ISNULL(P.ID, S.ID) AS RecordID,
    CASE 
        WHEN P.ID IS NULL THEN 'Missing in Production'
        WHEN S.ID IS NULL THEN 'Missing in Staging'
        WHEN P.RowHash <> S.RowHash THEN 'Data Mismatch'
        ELSE 'Synchronized'
    END AS ReconciliationStatus
FROM ProductionHash P
FULL OUTER JOIN StagingHash S ON P.ID = S.ID
WHERE P.RowHash <> S.RowHash 
   OR P.ID IS NULL 
   OR S.ID IS NULL
ORDER BY RecordID;
