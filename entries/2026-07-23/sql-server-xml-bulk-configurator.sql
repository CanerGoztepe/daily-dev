-- Table Assumption: CREATE TABLE SettingsTable (SettingKey NVARCHAR(50) PRIMARY KEY, SettingValue NVARCHAR(255));

DECLARE @xmlData XML = 
N'<Configuration>
    <Setting Key="MaxRetries" Value="5" />
    <Setting Key="Timeout" Value="30" />
    <Setting Key="EnableLogging" Value="true" />
</Configuration>';

BEGIN TRY
    BEGIN TRANSACTION;

    -- Merge the XML data into the physical table
    MERGE INTO SettingsTable AS Target
    USING (
        SELECT 
            T.c.value('@Key', 'NVARCHAR(50)') AS SettingKey,
            T.c.value('@Value', 'NVARCHAR(255)') AS SettingValue
        FROM @xmlData.nodes('/Configuration/Setting') AS T(c)
    ) AS Source
    ON Target.SettingKey = Source.SettingKey
    WHEN MATCHED THEN
        UPDATE SET Target.SettingValue = Source.SettingValue
    WHEN NOT MATCHED BY TARGET THEN
        INSERT (SettingKey, SettingValue)
        VALUES (Source.SettingKey, Source.SettingValue);

    -- Optional: Log the change if an Audit table exists
    -- INSERT INTO AuditLog (ActionDate, Details) VALUES (GETDATE(), 'Bulk XML Config Update Applied');

    COMMIT TRANSACTION;
    PRINT 'Settings successfully synchronized.';
END TRY
BEGIN CATCH
    IF @@TRANCOUNT > 0
        ROLLBACK TRANSACTION;

    DECLARE @ErrorMessage NVARCHAR(4000) = ERROR_MESSAGE();
    RAISERROR('Error during XML processing: %s', 16, 1, @ErrorMessage);
END CATCH;
