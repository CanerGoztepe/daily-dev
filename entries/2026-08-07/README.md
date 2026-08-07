# SQL Server Rolling 30-Day Retention Cohort Analysis

**Date:** 2026-08-07  
**Language:** Sql

## Description

Calculates daily user retention cohorts by identifying the first activity date per user and tracking subsequent activity over a rolling 30-day window.

## Usage

Replace 'UserActivity' with your table name containing columns 'UserId' and 'ActivityDate'. Run on any SQL Server instance to generate a retention heat map dataset.
