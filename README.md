# Daily Dev

A collection of small programming utilities and experiments.

| Date | Entry | Language | Description |
|---|---|---|---|
| 2026-07-13 | [File Size Aggregator](entries/2026-07-13/file-size-aggregator.py) | Python | A command-line tool that recursively calculates the total disk usage of a directory and lists subdirectories sorted by size. |
| 2026-07-14 | [Log Error Frequency Analyzer](entries/2026-07-14/log-error-frequency-analyzer.py) | Python | A utility that parses log files to count occurrences of specific error levels and extract the most frequent unique error messages. |
| 2026-07-16 | [SQL Server Orphaned Record Identifier](entries/2026-07-16/sql-server-orphaned-record-identifier.sql) | Sql | Identifies rows in a master table that lack corresponding records in a child table, useful for detecting referential integrity gaps without formal foreign keys. |
| 2026-07-17 | [SQL Server Whitespace Normalizer](entries/2026-07-17/sql-server-whitespace-normalizer.sql) | Sql | Standardizes inconsistent text data by stripping leading/trailing whitespace and collapsing multiple internal spaces into a single space. |
| 2026-07-18 | [SQL Server Duplicate Key Grouping and Cleanup Auditor](entries/2026-07-18/sql-server-duplicate-key-grouping-and-cleanup-auditor.sql) | Sql | Identifies duplicate rows based on a business key and generates a script to keep only the most recent entry while flagging others for review or deletion. |
| 2026-07-20 | [SQL Server Inventory Aging Bucket Analyzer](entries/2026-07-20/sql-server-inventory-aging-bucket-analyzer.sql) | Sql | Categorizes inventory stock into aging buckets based on the duration since the last movement date to help identify slow-moving or obsolete items. |
<!-- DAILY_ENTRIES -->
