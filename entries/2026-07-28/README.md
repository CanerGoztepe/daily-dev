# JSON Nested Key Flattener

**Date:** 2026-07-28  
**Language:** Python

## Description

Transforms deeply nested JSON objects into a single-level dictionary with dot-notation keys, perfect for preparing complex data for tabular export or database ingestion.

## Usage

Call flatten_json(data) with a dictionary; it returns a flattened dictionary where nested structure is represented by parent.child keys.
