# Commit Extractor for Vulnerability Lookup

## Overview

This project was developed during the Open Source Security Software Hackathon in Luxembourg (hackathon.lu), the objective was to have a way to extract from (the nvd json dump or others) commit information from the vulnerabilities fix references, so that we can latter link a cve patch to its respective patch code snippet and commit hash.

## Approach

The project explores two primary strategies for commit extraction:

### 1. Web Page Regex Parsing

Utilizes regular expressions to search through web page HTML:
- Provides better initial results compared to alternative methods, but still not good enough
- Challenges in accurately pinpointing commit codes within page structures

### 2. Large Language Model (LLM) Extraction

Attempts to use AI-powered extraction techniques:
- Extremely slow processing
- High rate of inaccurate results

## Current Status

**Work in Progress:** The project is currently facing challenges in achieving precise commit extraction with low false-positive rates.

## Limitations

- Regex method: Difficulty in precise commit code location
- LLM method: Slow performance and low accuracy
- High false-positive rates in both approaches

## Acknowledgments

Developed during the Luxembourg Open Source Security Software Hackathon