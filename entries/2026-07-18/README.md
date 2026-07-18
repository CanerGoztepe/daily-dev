# SQL Server Duplicate Key Grouping and Cleanup Auditor

**Date:** 2026-07-18  
**Language:** Sql

## Description

Identifies duplicate rows based on a business key and generates a script to keep only the most recent entry while flagging others for review or deletion.

## Usage

Replace 'TargetTable', 'BusinessKeyColumn', and 'TimestampColumn' with your actual schema. Run the script to generate a report of duplicates and their row-level identifiers.
