-- Assumes a table: [Transactions] (TransactionID INT, TransactionAmount DECIMAL(18,2))
WITH LeadingDigits AS (
    SELECT 
        LEFT(CAST(ABS(TransactionAmount) AS VARCHAR(20)), 1) AS LeadingDigit,
        COUNT(*) AS ActualCount,
        CAST(COUNT(*) AS FLOAT) / SUM(COUNT(*)) OVER () AS ActualFrequency
    FROM Transactions
    WHERE TransactionAmount <> 0
    GROUP BY LEFT(CAST(ABS(TransactionAmount) AS VARCHAR(20)), 1)
),
BenfordDistribution AS (
    SELECT * FROM (VALUES 
        ('1', 0.301), ('2', 0.176), ('3', 0.125), ('4', 0.097), 
        ('5', 0.079), ('6', 0.067), ('7', 0.058), ('8', 0.051), ('9', 0.046)
    ) AS B(Digit, ExpectedFrequency)
)
SELECT 
    B.Digit,
    B.ExpectedFrequency,
    ISNULL(L.ActualFrequency, 0) AS ActualFrequency,
    ABS(ISNULL(L.ActualFrequency, 0) - B.ExpectedFrequency) AS Deviation,
    CASE 
        WHEN ABS(ISNULL(L.ActualFrequency, 0) - B.ExpectedFrequency) > 0.1 
        THEN 'Significant Anomaly' 
        ELSE 'Within Normal Variance' 
    END AS RiskIndicator
FROM BenfordDistribution B
LEFT JOIN LeadingDigits L ON B.Digit = L.LeadingDigit
ORDER BY B.Digit;
