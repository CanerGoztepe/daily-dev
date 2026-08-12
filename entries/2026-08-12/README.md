# SQL Server Benford's Law Auditor

**Date:** 2026-08-12  
**Language:** Sql

## Description

Performs a digital analysis audit on financial transaction tables to detect potential fraud or manual data manipulation by identifying deviations from Benford's Law distribution.

## Usage

Replace 'TransactionAmount' and 'Transactions' with your specific financial column and table names. The query compares actual leading digit frequency against the theoretical Benford probability.
