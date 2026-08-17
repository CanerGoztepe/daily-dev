# Config-as-Code INI Semantic Validator

**Date:** 2026-08-17  
**Language:** Python

## Description

Validates an INI configuration file against a strict schema defining required sections, keys, and expected value types (integer, boolean, or string) to prevent runtime configuration errors.

## Usage

Define a schema dictionary where keys are section/key tuples and values are types. Pass the config file path to 'validate_config(file_path, schema)'.
