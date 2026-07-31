# Pandas-Free CSV Data Anonymizer

**Date:** 2026-07-31  
**Language:** Python

## Description

A lightweight utility that masks sensitive PII columns in a CSV file using SHA-256 hashing to ensure data privacy during testing or data sharing.

## Usage

Call anonymize_csv(input_path, output_path, sensitive_columns) passing a list of column names to hash.
