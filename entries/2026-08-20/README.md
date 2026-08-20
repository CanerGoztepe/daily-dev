# Local Process Port Auditor

**Date:** 2026-08-20  
**Language:** Python

## Description

Scans common local development ports to report which processes are currently binding to them to prevent 'Address already in use' deployment errors.

## Usage

Run 'python port_auditor.py' to print a table of common development ports (8000-8080) and the associated process IDs.
