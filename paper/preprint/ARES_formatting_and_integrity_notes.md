# ARES: Conflict Escalation Early Warning System
## Formatting, Bibliographic Verification, and Scientific Integrity Record

**Document Date:** October 2026  
**Document Status:** Working Preprint Audit Record  
**Target Manuscript:** `paper/preprint/ARES_preprint.docx`  
**Exported Document:** `paper/preprint/ARES_preprint.pdf`  
**Companion Files:** `paper/preprint/ARES_preprint.md`, `paper/preprint/REFERENCES.bib`  

---

### 1. Executive Summary & Document Overview

This record documents the structural reformatting, typographical standardization, bibliographic audit, and scientific integrity qualifications implemented for the research preprint **"ARES: Conflict Escalation Early Warning System"**.

The revised manuscript transforms the earlier draft into a rigorous, publication-grade academic research preprint formatted strictly in black and white according to conventional academic paper conventions (IEEE style, Times New Roman, A4 geometry, 1-inch margins). The document explicitly preserves the research boundaries and technical reality of the ARES codebase without overstating implementation status or inventing empirical results.

---

### 2. Title, Terminology, and Authorship Changes

#### 2.1 Title and Terminology
- **Exact Title Enforced:** `ARES: Conflict Escalation Early Warning System`.
- **Subtitle Removed:** The previous phrase *"spatio-temporal ingestion, feature modeling, and decision-support architecture"* has been eliminated from the primary title block.
- **Terminology Shift:** The word *"framework"* has been systematically replaced. ARES is described as a **system**, **early-warning system**, or **decision-support system** across all sections.
- **Acronym Expansion:** Preserved as established in project documentation: **ARES (Advanced Reconnaissance & Escalation System)**.

#### 2.2 Author Block and Affiliation
- **Author Block:** Exactly three authors are listed:
  1. **Tanya Deep** — USN: `1BY23IS231` — Email: `1BY23IS231@bmsit.in`
  2. **Shirin S. Hegde** — USN: `1BY23IS198` — Email: `1BY23IS198@bmsit.in`
  3. **Sreshta Karthikeyan** — USN: `1BY23IS215` — Email: `1BY23IS215@bmsit.in`
- **Institutional Affiliation:**  
  *Department of Information Science and Engineering, BMS Institute of Technology and Management, Bengaluru, Karnataka, India.*
- **Removed Elements:**
  - Removed all supervisor names, roles, designations, and supervisor contact details (`snehasureddy@bmsit.in`).
  - Removed student role labels, sub-team tags, and contribution percentages.
  - Eliminated placeholder ORCIDs and external contact channels.

---

### 3. Visual Styling and Typographical Standards

| Dimension | Specification | Implementation in Manuscript |
| :--- | :--- | :--- |
| **Color Palette** | Strictly Monochrome (Black & White) | 100% black text (`#000000`) and borders; no blue hyperlink text; no colored headings; no shaded table cells or callout boxes. |
| **Typeface** | Times New Roman | Applied universally across all headings, body text, tables, equation numbers, and references. |
| **Body Text** | 12 pt, Justified, ~1.5 Line Spacing | Line spacing set to 1.35–1.5; paragraph space after set to 4 pt; text alignment set to `JUSTIFY`. |
| **Title & Headings** | Hierarchical Bold Black | Title: 22 pt bold; Section Headings: 14 pt bold; Subsections: 12 pt bold. `keep_with_next` enforced to eliminate orphaned headings. |
| **Page Size & Margins** | A4, 1-inch margins | Page dimensions: 8.27 in × 11.69 in (210 mm × 297 mm); top, bottom, left, right margins set to 1.0 inch (1440 dxa). |
| **Header / Footer** | Clean Academic Pagination | Dynamic Word XML `<w:fldSimple w:instr="PAGE"/>` centered in footer. `different_first_page_header_footer = True` suppresses page number on Title Page (Page 1); Arabic numerals begin on Abstract (Page 2). |

---

### 4. Page and Section Structure Audit

To guarantee professional academic flow and prevent empty pages or fragmented tables in both Word and PDF, section breaks and table flows were engineered using native paragraph properties (`page_break_before = True`) rather than manual empty breaks.

#### 4.1 Page Allocation Summary (Total: 22 Pages)
- **Page 1 — Title Page:** Title, balanced author block, institutional affiliation, working paper metadata, and date.
- **Page 2 — Abstract & Keywords:** Single formal academic paragraph (no bullet points) synthesizing operational context, ingestion scope, fusion methodology, and prospective evaluation, followed by standardized IEEE-style keywords.
- **Pages 3–4 — Section 1: Introduction:** Operational challenge, three core gaps (temporal horizon mismatch, interpretability crisis, data heterogeneity), and explicit human-in-the-loop operational boundaries.
- **Pages 5–7 — Section 2: Related Work & Table I:** Comprehensive 5-domain literature review (conflict early warning, deep temporal graph networks, macroeconomic/climate multipliers, time-series anomaly detection, causal interpretability).
  - **Table I (Comparative Positioning):** Placed cleanly on Page 7 (`page_break_before = True`), keeping all 5 columns and 4 benchmark systems (ViEWS, ICEWS-RF, GDELT-Attention, ARES) intact without mid-table page splits.
- **Page 8 — Section 3: Research Gap and Contributions:** Nearest-neighbour analysis, structural gaps, and four concrete system contributions.
- **Page 9 — Section 4: Research Questions and Objectives:** Three formal research questions (RQ1–RQ3) and five targeted engineering objectives (O1–O5).
- **Page 10 — Section 5: System Architecture:** Modular Monolith architecture, 6-stage functional dataflow pipeline (`/ingestion`, `/preprocessing`, `/storage`, `/features`, `/model`, `/frontend & /api`), and enterprise monorepo synchronization.
- **Pages 11–12 — Section 6: Data Sources and Geographic Harmonization:**
  - **Page 11:** Narrative covering multi-source integration, canonical `Region_Key` geospatial harmonization (Zone A theater and Zone B sphere), and step-wise constant backward-fill temporal alignment.
  - **Page 12 — Table II (Data Sources & Licensing Constraints):** Placed cleanly on Page 12 (`page_break_before = True`), presenting all 12 data sources with operational coverage, ingestion modalities, reporting cadences, and open-access licensing terms intact on a single page.
- **Pages 13–14 — Section 7: Feature Engineering and Risk Scoring:** Detailed mathematical specifications for rolling features (event acceleration, tone volatility, protest escalation ratio, economic stress index, diplomatic silence duration), formal 0–100 Sigmoid Z-Score heuristic fusion formula, and unsupervised `IsolationForest` anomaly partitioning.
- **Page 15 — Section 8: Explainability and Human-in-the-Loop Decision Support:** Feature attribution ranking, dynamic evidence traceback to raw GDELT/ACLED URLs, and the cognitive triage analyst interface.
- **Page 16 — Section 9: Evaluation Protocol:** Leakage-free walk-forward time-series backtesting protocol, historical benchmark scenarios (2020 Galwan, 2022 Taiwan, 2021 Myanmar), reference baseline models, and statistical evaluation metrics.
- **Page 17 — Section 10: Results and Implementation Status & Table III:** Transparent qualification of system maturity.
  - **Table III (Implementation Status and Verification Audit):** Contained completely on Page 17, detailing all 13 subsystems with status classifications, codebase filepaths, and technical boundaries.
- **Page 18 — Section 11: Discussion:** Systems engineering trade-offs, false alarm mitigation, and operational viability for intelligence analysts.
- **Page 19 — Section 12: Limitations, Ethics, and Responsible Use:** Media coverage bias, reporting lags, non-causal heuristic indexing, dual-use risks, and open-access licensing compliance.
- **Page 20 — Section 13: Conclusion and Future Work:** Summary of engineering achievements and three-phase future research roadmap (empirical backtesting execution, Bayesian probability calibration, Temporal Graph Networks).
- **Pages 21–22 — References:** All 42 verified IEEE references formatted at 9 pt with 1.10 line spacing:
  - **Page 21:** References `[1]` to `[24]`.
  - **Page 22:** References `[25]` to `[42]`. Eliminates dangling 2-line final pages.

---

### 5. Tables and Mathematical Formulations

#### 5.1 Academic Table Formatting (Booktabs Standard)
- All tables adhere strictly to the academic booktabs specification:
  - Top border: single solid line, 12 pt (1.5 pt stroke width), black.
  - Header bottom border: single solid line, 6 pt (0.75 pt stroke width), black.
  - Bottom border: single solid line, 12 pt (1.5 pt stroke width), black.
  - Vertical interior and exterior borders: completely removed (`w:val="none"`).
  - Background fill / shading: completely removed (pure white `#FFFFFF`).
- Table rows carry `w:cantSplit` properties to prevent individual rows from breaking across page margins.
- Table headers carry `w:tblHeader` properties to guarantee proper repeating header behavior if viewed across page boundaries.
- Table captions are placed strictly **above** each table with bold label numbering (e.g., `TABLE I — COMPARATIVE POSITIONING...`).

#### 5.2 Mathematical Equations
- Mathematical formulations are typeset in Times New Roman italic font and rendered inside borderless two-column layout tables:
  - Left column: centered mathematical expression.
  - Right column: right-aligned bold equation numbering in parentheses: `(1)` through `(6)`.
- Key equations preserved:
  1. Equation (1): Event Acceleration $E_{\text{acc}}(t, W)$ with $\max(\cdot, 1)$ denominator protection.
  2. Equation (2): Tone Volatility $T_{\text{vol}}(t, W)$ standard deviation formulation.
  3. Equation (3): Protest Escalation Ratio $P_{\text{trans}}(t, W)$.
  4. Equation (4): Economic Stress Composite $S_{\text{econ}}(t, q)$.
  5. Equation (5): Diplomatic Silence Duration $D_{\text{silence}}(t)$.
  6. Equation (6): Domain-Calibrated Sigmoid Z-Score Fusion Score $S_{\text{composite}}(t) \in [0, 100]$.

---

### 6. Bibliographic Audit and Citation Verification (IEEE Style)

All 42 references in the manuscript were audited for bibliographic accuracy, relevance, and formatting consistency:
- **Style:** IEEE numerical order of appearance (`[1]`, `[2]`, ... `[42]`).
- **Completeness:** Every citation in the manuscript body has a corresponding entry in the References list, and every reference in the list is actively cited in the body.
- **Verification Summary:**
  - **Conflict Forecasting & Event Registries:** ViEWS (Hegre et al., *JPR* 2019 `[1]`, 2018 `[2]`, *ISQ* 2019 `[3]`); ICEWS (Ward et al., *ISR* 2013 `[4]`; Boschee et al., *Harvard Dataverse* `[9]`); Spatio-temporal modeling (Brandt et al., *JCR* 2016 `[5]`); Rare-event ML (Muchlinski et al., *Pol. Anal.* 2016 `[6]`); ACLED (Raleigh et al., *JPR* 2010 `[7]`); GDELT (Leetaru & Schrodt, *ISA* 2013 `[8]`); UCDP GED (Sundberg & Melander, *JPR* 2013 `[10]`; Gleditsch et al., *JPR* 2002 `[11]`; Chojnacki et al., *Int. Interact.* 2012 `[12]`).
  - **Dynamic Graph & Sequence Architectures:** Temporal Graph Networks (Rossi et al., *arXiv* 2020 `[13]`); EvolveGCN (Pareja et al., *AAAI* 2020 `[14]`); DyRep (Trivedi et al., *ICML* 2019 `[15]`); Know-Evolve (Trivedi et al., *ICML* 2017 `[16]`); GNN forecasting survey (Ma et al., *ACM CSUR* 2023 `[17]`); Meta-graphs (Campedelli et al., *AI & Law* 2021 `[18]`); Precursor attention networks (Hossain et al., *AAAI* 2023 `[19]`); GCN (Kipf & Welling, *ICLR* 2017 `[20]`); GAT (Veličković et al., *ICLR* 2018 `[21]`); TGAT (Xu et al., *ICLR* 2020 `[22]`).
  - **NLP, Transformers & Sentiment:** BERT (Devlin et al., *NAACL* 2019 `[23]`); RoBERTa (Liu et al., *arXiv* 2019 `[24]`); DistilBERT (Sanh et al., *NeurIPS-W* 2019 `[25]`); Multilingual sentiment (Banea et al., *ACL* 2014 `[26]`); VADER (Hutto & Gilbert, *ICWSM* 2014 `[27]`); Transformer architecture (Vaswani et al., *NeurIPS* 2017 `[28]`); GPT-2 (Radford et al., *OpenAI* 2019 `[29]`); Sentence-BERT (Reimers & Gurevych, *EMNLP* 2019 `[30]`).
  - **Time Series, Anomaly Detection & Causal Inference:** TFT (Lim et al., *Int. J. Forecast.* 2021 `[31]`); DeepAR (Salinas et al., *Int. J. Forecast.* 2020 `[32]`); Time-series transformers (Zerveas et al., *KDD* 2021 `[33]`); Isolation Forest (Liu et al., *IEEE ICDM* 2008 `[34]`); Causal representation learning (Schölkopf et al., *Proc. IEEE* 2021 `[41]`); Heterogeneous treatment effects (Athey & Imbens, *JEP* 2022 `[42]`).
  - **Macroeconomic & Environmental Multipliers:** Climate & conflict (Mach et al., *Nature* 2019 `[35]`; Hsiang et al., *Science* 2013 `[36]`; Burke et al., *Nature* 2015 `[37]`); Economic shocks & civil conflict (Miguel et al., *JPE* 2004 `[38]`); Greed & grievance (Collier & Hoeffler, *OEP* 2004 `[39]`); Insurgency & ethnicity (Fearon & Laitin, *APSR* 2003 `[40]`).

---

### 7. Scientific Integrity and Implementation Reality Record

In accordance with strict academic integrity mandates, the manuscript enforces the following scientific boundaries:

1. **Heuristic Indexing vs. Probabilistic Forecasting:**
   - The composite risk score $S_{\text{composite}} \in [0, 100]$ is formally documented as a **domain-calibrated heuristic decision-support index**, not a calibrated Bayesian posterior probability $P(\text{Escalation} \mid X)$.
   - The manuscript explicitly records that while sigmoid normalization bounds each $Z$-score to $(0, 1)$, linear combinations of sigmoids do not yield statistically calibrated probability distributions without post-hoc empirical calibration (e.g., Platt scaling or isotonic regression).

2. **No Fabricated Performance Claims:**
   - The manuscript reports **zero fabricated empirical metrics**: no invented ROC-AUC scores, no simulated warning lead times (e.g., "forecasts crises 14 days in advance"), and no unsubstantiated false-alarm suppression rates.
   - Section 9 formalizes a **prospective experimental protocol** designed to benchmark these exact metrics during future empirical backtesting.

3. **Subsystem Operational Reality:**
   - **Operational & Verified in Codebase:**
     - Live REST ingestion for GDELT 2.0, World Bank API, IMF DataMapper, UCDP GED, and ReliefWeb (`src/live_data.py`).
     - Static historical ingestion generators for ACLED, ICEWS, SIPRI, and UN Sanctions (`src/static_data_generator.py`).
     - Relational persistence via SQLite `master_data.db` (`src/database.py`).
     - Rolling feature extraction for acceleration, volatility, protest transition, and economic stress (`src/feature_engineering.py`).
     - Sigmoid $Z$-score heuristic scoring and `IsolationForest(contamination=0.10)` anomaly partitioning (`src/feature_engineering.py`).
     - Five-page interactive Streamlit analyst dashboard on port 8000 with Plotly geospatial visualizers (`app.py`, `artifacts/ares-dashboard/app.py`).
     - Direct URL traceback linking risk alerts to raw GDELT news records.
   - **Architecturally Specified but Not Yet Operational:**
     - Supervised machine learning classifiers (RandomForest, XGBoost) and deep NLP transformer heads (DistilBERT), which are specified in system architecture but currently bypassed in favor of heuristic sigmoid fusion.
     - Production PostGIS database deployment (`ST_Contains` spatial joins), which is currently modeled via indexed relational attribute lookup tables.
   - **Partially Implemented:**
     - Express 5 TypeScript REST API monorepo (`artifacts/api-server/`, `lib/`), which provides REST schemas but runs alongside the primary Python pipeline.

---

### 8. Verification and Quality Checks Performed

- [x] **Word Document Generation:** Generated cleanly via `python paper/preprint/generate_academic_preprint.py` with zero COM automation errors.
- [x] **PDF Document Export:** Converted natively via Microsoft Word 16.0 COM interface (`win32com.client`), ensuring 100% typographic fidelity with the Word layout engine.
- [x] **PDF Page-by-Page Audit:** All 22 pages audited programmatically and visually via `pypdf`:
  - Page 1 contains only the Title, Authors, Affiliation, and Working Document notice.
  - Page 2 contains only the Abstract and Keywords.
  - Pages 3–20 contain Sections 1 through 13 with all major sections starting on intended new pages.
  - Tables I, II, and III are completely contained on single pages with zero orphaned rows.
  - Pages 21–22 contain all 42 references without dangling overflow onto Page 23.
- [x] **Monochrome Compliance:** Universal removal of color styles, fills, tints, and borders.
- [x] **Supervisory Independence:** Complete removal of supervisor names, designations, and contact emails.
- [x] **Integrity Audit:** Complete preservation of technical boundaries, heuristic index definitions, and prospective protocol status.
