# Log Latency Spike Detector

**Date:** 2026-08-02  
**Language:** Python

## Description

Analyzes application log files to identify time-gaps between consecutive log entries that exceed a defined threshold, helping to pinpoint performance bottlenecks.

## Usage

python log_analyzer.py <path_to_log> <threshold_seconds>. The log lines must contain an ISO-8601 timestamp at the start.
