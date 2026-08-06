# SQL Server Fuzzy Duplicate Contact Detector

**Date:** 2026-08-06  
**Language:** Sql

## Description

Identifies potential duplicate customer records by comparing names using the Soundex algorithm and phone number parity to catch typos and variation errors.

## Usage

Execute in SQL Server Management Studio on a database containing a 'Customers' table with 'FirstName', 'LastName', and 'PhoneNumber' columns.
