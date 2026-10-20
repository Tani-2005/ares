# ARES Living Preprint Repository
### *ARES: An Explainable Multi-Source Data Fusion Framework for Conflict Escalation Early Warning*

[![Preprint Version: 1.0.0](https://img.shields.io/badge/Preprint-v1.0.0--preprint-blue.svg)](#)
[![Status: Foundational Framework](https://img.shields.io/badge/Status-Framework%20%26%20Protocol-orange.svg)](#)
[![Peer Review: Open Preprint](https://img.shields.io/badge/Review-Self--Audited%20Preprint-success.svg)](#)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

---

## 📌 Overview

This directory contains the **living preprint** for **ARES (Advanced Reconnaissance & Escalation System)**. 

The manuscript is designed as a modular, academically defensible publication that documents the complete system architecture, multi-source data ingestion pipeline, mathematical feature engineering formulas, and prospective evaluation protocol. It is structured so that prospective empirical evaluations and experimental results can be incorporated incrementally without rewriting the foundational methodology.

---

## 📄 File Inventory

| Filename | Format | Description |
|---|---|---|
| [`ARES_preprint.docx`](ARES_preprint.docx) | Microsoft Word (.docx) | Complete, professionally styled academic manuscript ready for distribution, submission, or graduate school application portfolios. |
| [`ARES_preprint.md`](ARES_preprint.md) | Markdown (.md) | Full-text version-controlled source of the manuscript with complete LaTeX math blocks, tables, and citations. |
| [`REFERENCES.bib`](REFERENCES.bib) | BibTeX (.bib) | Verified bibliography containing 42 peer-reviewed citations with full metadata and DOIs. |
| [`CHANGELOG.md`](CHANGELOG.md) | Markdown (.md) | Detailed audit log of revisions, methodological qualifications, and scientific integrity corrections. |
| [`README.md`](README.md) | Markdown (.md) | This guide: versioning, roadmap, and update instructions. |

---

## 🎯 Scope & Academic Positioning

### Intended Use:
- **Graduate School Applications**: Serves as a transparent, rigorous writing sample for MSc/PhD applications in Data Science, Applied AI, Computational Social Science, and Geospatial Analytics.
- **Academic Preprint Hosting**: Formatted for submission to open-access repositories (e.g., arXiv, TechRxiv, SSRN).
- **Project Progress Foundation**: Provides a clear roadmap for completing the historical backtesting experiments without compromising scientific honesty.

### Scientific Integrity Principles:
1. **Separation of Architecture from Evaluation**: System architecture and data-fusion implementations are documented as engineering achievements; empirical predictive accuracy and lead times are formalized strictly as a **prospective evaluation protocol** until historical backtesting is executed.
2. **Heuristic Calibration vs. Empirical Learning**: Feature weights ($w_k$) and threshold tiers (Green/Amber/Red) are explicitly stated as domain-informed heuristic baselines rather than learned model parameters.
3. **Attribution vs. Causation**: Model feature importances are identified as statistical associations, not causal proofs.

---

## 🔄 Instructions for Updating the Preprint

When historical backtesting experiments or model retraining are conducted, update the preprint following these steps:

### Step 1: Execute Historical Backtesting
1. Select crisis cases from the documented Indo-Pacific backtesting catalog (e.g., 2020 Galwan Valley, 2022 Taiwan Strait tensions).
2. Set historical cutoff date $T_{\text{cutoff}}$ strictly prior to crisis peak ($T_{\text{peak}}$) to prevent temporal leakage.
3. Compute prospective evaluation metrics:
   - Precision-Recall Area Under the Curve (PR-AUC)
   - Brier Score (calibration error)
   - Early Warning Lead Time ($T_{\text{peak}} - T_{\text{first alert}}$ in days)
   - False Positive Rate (FPR) during pre-crisis stable periods.

### Step 2: Update Section 10 ("Results and Implementation Status")
1. In `ARES_preprint.md`, replace the prospective declaration in Section 10 with a dedicated subsection:
   `10.1 Empirical Backtesting Performance on Indo-Pacific Benchmark Cases`.
2. Insert the verified results table detailing metrics across lookback windows (7d, 14d, 30d).
3. Include an ablation study comparing single-source models against the multi-source fusion engine.

### Step 3: Update Abstract & Conclusion
1. Add 1–2 sentences summarizing the verified empirical lead times and recall rates.
2. Ensure no unverified claims exceed the logged data.

### Step 4: Re-generate `ARES_preprint.docx`
Run the generation script from the project root:
```bash
python paper/preprint/generate_docx_manuscript.py
```

### Step 5: Log the Changes in `CHANGELOG.md`
Record the date, experimental parameters, dataset version, and specific metrics added under a new version tag (e.g., `[Version 1.1.0-empirical]`).

---

## 👥 Authors & Affiliation

- **Tanya Deep** (`USN: 1BY23IS231`) — *System Development & Visualization Lead*
- **Shirin S. Hegde** (`USN: 1BY23IS198`) — *Data Engineering & Integration Lead*
- **Sreshta Karthikeyan** (`USN: 1BY23IS215`) — *AI/ML Model Developer*
- **Prof. Sneha Sureddy** — *Assistant Professor & Project Guide*

**Department of Information Science and Engineering**  
BMS Institute of Technology and Management (BMSIT&M)  
Autonomous Institute under Visvesvaraya Technological University (VTU)  
Bengaluru, Karnataka, India
