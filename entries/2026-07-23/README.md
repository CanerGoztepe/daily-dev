# SQL Server XML Bulk Configurator

**Date:** 2026-07-23  
**Language:** Sql

## Description

Parses a configuration XML string to perform bulk updates on a settings table, ensuring atomic operations by validating node existence.

## Usage

Pass an XML string into the @xmlData variable to update settings defined in the SettingsTable (Columns: SettingKey, SettingValue).
