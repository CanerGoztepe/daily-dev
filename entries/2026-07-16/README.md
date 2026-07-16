# SQL Server Orphaned Record Identifier

**Date:** 2026-07-16  
**Language:** Sql

## Description

Identifies rows in a master table that lack corresponding records in a child table, useful for detecting referential integrity gaps without formal foreign keys.

## Usage

Replace 'Orders' and 'OrderDetails' with your target tables. Run the query in SSMS to generate a list of orphaned OrderIDs for cleanup or auditing.
