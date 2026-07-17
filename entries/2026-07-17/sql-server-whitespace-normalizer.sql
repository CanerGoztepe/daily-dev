/* 
Assumption: The table contains a column with 'dirty' string data (e.g., '  John   Doe  ').
Goal: Transform to 'John Doe'.
*/

DECLARE @TargetTable NVARCHAR(128) = 'Users';
DECLARE @TargetColumn NVARCHAR(128) = 'FullName';
DECLARE @SQL NVARCHAR(MAX);

-- Validate table and column exist to prevent injection and runtime errors
IF EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID(@TargetTable) AND name = @TargetColumn)
BEGIN
    SET @SQL = N'
    UPDATE ' + QUOTENAME(@TargetTable) + ' 
    SET ' + QUOTENAME(@TargetColumn) + ' = 
        -- Step 3: Replace multiple spaces with a single space
        REPLACE(
            REPLACE(
                REPLACE(
                    LTRIM(RTRIM(' + QUOTENAME(@TargetColumn) + ')), 
                ''  '', '' *''), 
            ''* '', ''''), 
        ''*'', '''')
    WHERE ' + QUOTENAME(@TargetColumn) + ' LIKE ''%  %'' 
       OR ' + QUOTENAME(@TargetColumn) + ' LIKE '' %'' 
       OR ' + QUOTENAME(@TargetColumn) + ' LIKE ''% ''';

    -- Execute the sanitization
    EXEC sp_executesql @SQL;
    
    SELECT 'Cleanup successful' AS Status;
END
ELSE
BEGIN
    RAISERROR('Target table or column not found in schema.', 16, 1);
END;
