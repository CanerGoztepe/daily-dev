# SQL Server Numeric Outlier Sensitivity Auditor

**Date:** 2026-07-24  
**Language:** Sql

## Description

Identifies numerical data points that deviate significantly from the mean using the Z-Score method to detect potential input errors or extreme anomalies.

## Usage

Replace 'TargetTable', 'ValueColumn', and 'CategoryColumn' with your data, then execute the query to inspect records with a Z-Score greater than 3.0.
