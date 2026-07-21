# SQL Server Schema Drift Detector

**Date:** 2026-07-21  
**Language:** Sql

## Description

Compares current table column definitions against a baseline stored in a metadata table to identify unexpected changes in data types, lengths, or nullability.

## Usage

Create the 'SchemaBaseline' table, insert expected metadata, and run this script to generate an alert report for any columns that have drifted from the baseline.
