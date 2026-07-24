-- Assumes a table 'FinancialMetrics' with columns: [Id], [Category], [TransactionAmount]
-- This script detects statistical outliers that may indicate manual entry errors or system bugs

WITH Stats AS (
    SELECT 
        Category,
        AVG(CAST(TransactionAmount AS FLOAT)) AS AvgValue,
        STDEV(CAST(TransactionAmount AS FLOAT)) AS StdDevValue
    FROM FinancialMetrics
    GROUP BY Category
),
ZScoreCalculation AS (
    SELECT 
        m.Id,
        m.Category,
        m.TransactionAmount,
        s.AvgValue,
        s.StdDevValue,
        (CAST(m.TransactionAmount AS FLOAT) - s.AvgValue) / NULLIF(s.StdDevValue, 0) AS ZScore
    FROM FinancialMetrics m
    INNER JOIN Stats s ON m.Category = s.Category
)
SELECT 
    Id,
    Category,
    TransactionAmount,
    ROUND(ZScore, 2) AS ZScore,
    CASE 
        WHEN ABS(ZScore) > 3 THEN 'Extreme Outlier'
        WHEN ABS(ZScore) > 2 THEN 'Warning'
        ELSE 'Normal'
    END AS SeverityLevel
FROM ZScoreCalculation
WHERE ABS(ZScore) > 2
ORDER BY ABS(ZScore) DESC;

/*
Logic Explanation:
1. 'Stats' CTE calculates the Mean and Standard Deviation per Category.
2. 'ZScoreCalculation' CTE determines how many standard deviations a value is from the mean.
3. The final SELECT filters for records exceeding 2 standard deviations (Z > 2), 
   flagging them for manual review as they likely represent abnormal system behavior 
   or erroneous data entry.
*/
