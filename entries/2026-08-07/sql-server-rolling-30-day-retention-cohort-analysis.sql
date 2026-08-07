-- Assumes table UserActivity (UserId INT, ActivityDate DATE)
WITH UserFirstActivity AS (
    -- Find the day each user joined
    SELECT 
        UserId, 
        MIN(ActivityDate) AS CohortMonth
    FROM UserActivity
    GROUP BY UserId
),
RetentionGrid AS (
    -- Join activity to cohorts and calculate day offset
    SELECT 
        uf.CohortMonth,
        DATEDIFF(DAY, uf.CohortMonth, ua.ActivityDate) AS DayOffset,
        ua.UserId
    FROM UserActivity ua
    INNER JOIN UserFirstActivity uf ON ua.UserId = uf.UserId
    WHERE DATEDIFF(DAY, uf.CohortMonth, ua.ActivityDate) BETWEEN 0 AND 30
)
-- Pivot or aggregate the results into a cohort analysis format
SELECT 
    CohortMonth,
    COUNT(DISTINCT CASE WHEN DayOffset = 0 THEN UserId END) AS NewUsers,
    COUNT(DISTINCT CASE WHEN DayOffset = 1 THEN UserId END) AS Day1_Retained,
    COUNT(DISTINCT CASE WHEN DayOffset = 7 THEN UserId END) AS Day7_Retained,
    COUNT(DISTINCT CASE WHEN DayOffset = 30 THEN UserId END) AS Day30_Retained,
    CAST(COUNT(DISTINCT CASE WHEN DayOffset = 30 THEN UserId END) AS FLOAT) / 
    NULLIF(COUNT(DISTINCT CASE WHEN DayOffset = 0 THEN UserId END), 0) AS RetentionRate30
FROM RetentionGrid
GROUP BY CohortMonth
ORDER BY CohortMonth DESC;
