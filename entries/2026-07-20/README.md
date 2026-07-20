# SQL Server Inventory Aging Bucket Analyzer

**Date:** 2026-07-20  
**Language:** Sql

## Description

Categorizes inventory stock into aging buckets based on the duration since the last movement date to help identify slow-moving or obsolete items.

## Usage

Execute against a schema containing a table named InventoryMovements with columns [ItemID], [Quantity], and [LastMovementDate].
