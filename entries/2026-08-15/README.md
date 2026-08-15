# CSV Column Schema Enforcer

**Date:** 2026-08-15  
**Language:** Python

## Description

A utility that verifies a CSV file matches a strictly defined header order and data type schema, flagging rows that deviate from the expected structure before further processing.

## Usage

Define a schema dictionary with column names and types, then pass the file path to the validator. It returns a report of missing columns or type-mismatch rows.
