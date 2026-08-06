-- Assumptions: Table [dbo].[Customers] (CustomerID INT, FirstName VARCHAR(100), LastName VARCHAR(100), PhoneNumber VARCHAR(20))

WITH NormalizedData AS (
    SELECT 
        CustomerID,
        FirstName,
        LastName,
        SOUNDEX(FirstName) AS NameSoundex,
        -- Remove non-numeric characters from phone for comparison
        REPLACE(REPLACE(REPLACE(REPLACE(PhoneNumber, '(', ''), ')', ''), '-', ''), ' ', '') AS CleanPhone
    FROM [dbo].[Customers]
)
SELECT 
    A.CustomerID AS OriginalID,
    B.CustomerID AS PotentialDuplicateID,
    A.FirstName + ' ' + A.LastName AS OriginalName,
    B.FirstName + ' ' + B.LastName AS DuplicateName,
    A.CleanPhone AS Phone
FROM NormalizedData A
JOIN NormalizedData B 
    ON A.NameSoundex = B.NameSoundex 
    AND A.CleanPhone = B.CleanPhone
    AND A.CustomerID < B.CustomerID -- Ensures we only see unique pairs once
ORDER BY A.CleanPhone, A.LastName;
