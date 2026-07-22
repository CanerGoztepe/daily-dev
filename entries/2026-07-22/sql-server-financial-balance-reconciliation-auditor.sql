-- Assumes Tables:
-- LedgerHeader: (AccountId, AccountName, RecordedBalance)
-- LedgerEntries: (EntryId, AccountId, Amount, EntryDate)

WITH CalculatedBalances AS (
    SELECT 
        h.AccountId, 
        h.AccountName,
        h.RecordedBalance,
        SUM(ISNULL(e.Amount, 0)) AS CalculatedBalance,
        COUNT(e.EntryId) AS TransactionCount
    FROM LedgerHeader h
    LEFT JOIN LedgerEntries e ON h.AccountId = e.AccountId
    GROUP BY h.AccountId, h.AccountName, h.RecordedBalance
)
SELECT 
    AccountId,
    AccountName,
    RecordedBalance,
    CalculatedBalance,
    (RecordedBalance - CalculatedBalance) AS Discrepancy,
    CASE 
        WHEN ABS(RecordedBalance - CalculatedBalance) > 0.01 THEN 'CRITICAL: Out of Balance'
        WHEN TransactionCount = 0 AND RecordedBalance <> 0 THEN 'WARNING: No transactions for non-zero balance'
        ELSE 'OK'
    END AS ReconciliationStatus
FROM CalculatedBalances
WHERE ABS(RecordedBalance - CalculatedBalance) > 0.01 
   OR (TransactionCount = 0 AND RecordedBalance <> 0)
ORDER BY ABS(Discrepancy) DESC;
