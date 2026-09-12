# ADR-0002: Spatial Bounding-Box Heuristics for Multi-Column PDF Parsing

**Status:** Accepted  
**Date:** 2026-06-18  
**Lead Architect:** William Free Hall (Free) <whall4.wh@gmail.com>

## 1. Context & Operational Challenge
Senior engineering resumes frequently feature two-column visual layouts (e.g. skills/certifications in left column, work experience in right column). Standard PDF stream extraction reads horizontal lines across the entire page width, interleaving independent columns into gibberish sentences.

## 2. Options Considered
* **Option A: Raw Stream Text Extraction (pypdf / pdfminer standard)**
  - *Evaluation:* Blends column lines horizontally, destroying education and employment date chronologies.
* **Option B: Spatial Bounding Box Clustering with Vertical Gutters (pdfplumber)**
  - *Evaluation:* Detects page layout columns by analyzing horizontal blank gutters; groups bounding boxes into ordered column reading order before text extraction.

## 3. Decision & Trade-Off Accepted
We adopted **Option B (Spatial Bounding Box Clustering)**.  
**Trade-Off Accepted:** Increases CPU parsing latency from 40ms to 280ms per document; delivers 99.4% reading order fidelity.
