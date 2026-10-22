# ARES: Conflict Escalation Early Warning System
## Scientific Integrity Audit, Verification Analysis, and Implementation Caveats

**Document Date:** October 2026  
**Document Status:** Official Preprint Integrity Audit  
**Target Manuscript:** `paper/preprint/ARES_preprint.tex` (`ARES_preprint.pdf`)  
**Document Class:** Elsevier `elsarticle.cls` (Preprint, 12pt)  

---

### 1. Executive Statement on Scientific Integrity

This audit record accompanies the Elsevier `elsarticle` LaTeX preprint of **ARES: Conflict Escalation Early Warning System**. 

The purpose of this audit is to enforce uncompromising scientific rigor, academic honesty, and transparency. In computational conflict forecasting and predictive intelligence, overstating software maturity or claiming predictive validation before empirical execution poses severe ethical and operational risks. This audit establishes a clear line between:
1. **Implemented and functionally verified software capabilities** within the existing codebase.
2. **Specified architectural components** that have formal engineering designs but rely on heuristics or mock layers in the current demonstrator.
3. **Prospective evaluation protocols** designed for rigorous validation versus empirical results that remain in-progress.

---

### 2. Implementation Status vs. Architectural Specification

The following matrix documents the exact technical reality of every major subsystem in the ARES project:

| Subsystem / Component | Documented Architectural Design | Current Codebase Implementation Status | Operational Verification Location | Technical Boundaries & Caveats |
| :--- | :--- | :--- | :--- | :--- |
| **Live OSINT Ingestion** | Asynchronous parallel fetchers for GDELT 2.0, World Bank, IMF, UCDP GED, and ReliefWeb. | **Implemented & Verified** | `src/live_data.py` | Active REST endpoints with exponential backoff and payload hashing. Dependent on upstream API availability and GDELT 15-minute cadence. |
| **Historical Baseline Ingestion** | Synthetic and historical ingestion generators for ACLED, ICEWS, SIPRI, and UN Sanctions. | **Implemented & Verified** | `src/static_data_generator.py` | Local database generator populating $\sim$10,000 historical records for development and demonstration. |
| **Relational Storage Layer** | Dual-tier storage: SQLite for local demonstrator, PostgreSQL + PostGIS for enterprise deployment. | **Implemented & Verified** (SQLite) | `src/database.py` | Operational SQLite relational database (`master_data.db`). Full PostGIS spatial schema is designed but not deployed. |
| **Geographic Harmonization** | Canonical `Region_Key` schema partitioning monitored space into Zone A (conflict theater) and Zone B (influence sphere). | **Implemented & Verified** | `src/feature_engineering.py` | Coordinate and country entity normalization mapped via atomic dictionary lookups (e.g., `ZoneA_IND`, `ZoneA_CHN`). |
| **Temporal Frequency Synchronization** | Step-wise backward-fill (carry-forward) strategy aligning quarterly macroeconomics with daily news/events. | **Implemented & Verified** | `src/feature_engineering.py` | Quarterly GDP/CPI values establish a 90-day baseline over which daily deviations are computed. |
| **Rolling Feature Extraction** | Multi-horizon extraction ($W \in \{7, 14, 30\}$ days) of event acceleration, tone volatility, protest ratio, economic stress, and diplomatic silence. | **Implemented & Verified** | `src/feature_engineering.py` | Mathematical algorithms functional; denominator bounded by $\max(\cdot, 1)$ to eliminate zero-division anomalies. |
| **Sigmoid Z-Score Fusion Engine** | Domain-weighted logistic sigmoid transformation generating continuous 0--100 escalation risk scores. | **Implemented & Verified** | `src/feature_engineering.py` | Verified computation mapping standardized feature Z-scores into Green (0--32), Amber (33--65), and Red (66--100) operational tiers. |
| **Unsupervised Anomaly Detector** | `IsolationForest` ($contamination=0.10$, $n\_estimators=100$) isolating non-linear multi-variable outliers. | **Implemented & Verified** | `src/feature_engineering.py` | Scikit-learn integration operational; flags top 10\% multi-dimensional feature outliers for priority analyst audit. |
| **Analyst Decision Dashboard** | Interactive multi-view web application for mission status, heatmaps, 90-day trendlines, and source feeds. | **Implemented & Verified** | `app.py` | Functional 5-page Streamlit application on port 8000 using Plotly for interactive data exploration. |
| **Source Evidence Traceability** | Dynamic URL traceback linking risk scores directly to raw GDELT news articles and ACLED incident logs. | **Implemented & Verified** | `app.py` | Traceback links functional; enables human analyst verification in under two minutes. |
| **Supervised Machine Learning Head** | Random Forest and XGBoost classifiers with SMOTE class rebalancing for binary conflict onset prediction. | *Architecturally Specified / Unimplemented* | Project SRS §3.4; Architecture §3.2 | Specified in system documentation; operational demonstrator currently bypasses supervised classification in favor of heuristic Sigmoid Fusion. |
| **Deep NLP Sentiment Head** | Fine-tuned DistilBERT / RoBERTa transformer model for localized diplomatic text classification. | *Architecturally Specified / Unimplemented* | Project SRS §3.4; Tech Stack | Specified in technical requirements; demonstrator currently utilizes pre-computed GDELT Tone and Goldstein metrics. |
| **Full PostGIS Containment Joins** | `ST_Contains` spatial joins across ESRI shapefiles for precise subnational polygon resolution. | *Architecturally Specified / Unimplemented* | Architecture Doc §2.1 | Specified in enterprise design; demonstrator uses standardized tabular lookup tables. |
| **Enterprise TypeScript API Monorepo** | Express 5 REST API with Drizzle ORM and OpenAPI code generation. | *Partially Implemented* | `artifacts/api-server/`, `lib/` | Express 5 server and Drizzle schemas created; operates alongside Python core pipeline. |
| **Historical Walk-Forward Backtesting** | Leakage-free time-series backtest across 2020 Galwan, 2022 Taiwan, and 2021 Myanmar crises. | *Protocol Formalized / Execution In-Progress* | Section 9 of Manuscript | Full experimental methodology formalized; empirical backtesting execution and metric extraction remain ongoing. |

---

### 3. Methodological Qualifications and Epistemic Bounds

#### 3.1 Heuristic Decision-Support Index vs. Bayesian Probability
- **The Finding:** The composite score generated by Equation~(6) in the manuscript:
  $$\text{Risk\_Score} = \frac{100}{1 + \exp\left(-\sum_{k=1}^K w_k Z_k\right)}$$
  produces a continuous value between 0 and 100.
- **The Qualification:** This score is **not** a calibrated posterior probability $P(\text{Escalation} \mid X)$. The weights ($w_1 = 0.30, w_2 = 0.20, w_3 = 0.15, w_4 = 0.15, w_5 = 0.10, w_6 = 0.10$) represent domain-informed qualitative heuristics derived from conflict literature, not maximum-likelihood estimators fit on empirical data.
- **Scientific Implication:** Linear combinations of logistic sigmoids do not yield statistically calibrated likelihood distributions without empirical post-hoc calibration (e.g., Platt scaling or isotonic regression). The manuscript explicitly labels this index as a *decision-support ranking tool* rather than a probabilistic forecast.

#### 3.2 Attribution vs. Causality
- **The Distinction:** In the ARES dashboard, feature attribution breakdowns (e.g., ``Event Acceleration contributed 52% of score elevation'') reflect the mathematical decomposition of the linear sum $\sum w_k Z_k$.
- **The Caveat:** Statistical feature contribution does not establish causal directionality. Escalation may be driven by unobserved political factors that simultaneously cause media coverage and troop movements. ARES explicitly labels these breakdowns as *Contributing Observed Indicators* to prevent analysts from making invalid causal inferences.

---

### 4. Resolution of Unsupported Claims from Earlier Drafts

Earlier project drafts contained preliminary or aspirational statements that have been audited and corrected in the current Elsevier preprint:

1. **Premature Backtest Results Removed:**
   - *Earlier Draft Statement:* ``Historical backtesting on Indo-Pacific crisis cases demonstrates that ARES achieves a Recall of $\ge 75\%$, a False Positive Rate of $< 15\%$, and provides positive early-warning lead times of 7 to 21 days.''
   - *Audit Finding:* Empirical backtesting across multi-year historical GDELT/ACLED datasets has not yet completed full execution. Claiming $\ge 75\%$ recall as a demonstrated empirical result was premature.
   - *Resolution in Current Preprint:* These values are formally repositioned as **Target Benchmark Objectives** within a prospective evaluation protocol (Section~9), with an explicit notice that empirical execution is in-progress.

2. **Acronym and Title Integrity:**
   - *Earlier Draft Statement:* ``ARES: An Explainable Multi-Source Data Fusion Framework for Conflict Escalation Early Warning: Spatio-temporal ingestion, feature modeling, and decision-support architecture.''
   - *Resolution in Current Preprint:* Standardized to the exact title: **``ARES: Conflict Escalation Early Warning System''**. The subtitle was eliminated, and the term ``framework'' was replaced with ``system'' or ``early-warning system'' throughout to accurately reflect the software implementation.

3. **Supervisory and Role Disclosures:**
   - *Earlier Draft Statement:* Listed university supervisor designations, emails, and student sub-team contribution tags.
   - *Resolution in Current Preprint:* Student USNs are formatted strictly in lowercase within institutional email addresses (`1by23is198@bmsit.in`, `1by23is215@bmsit.in`, `1by23is231@bmsit.in`) in ascending order. All external supervisor details and administrative tags were removed for preprint neutrality.

---

### 5. Bibliographic Audit (IEEE Numbered Style)

All 42 references in `references.bib` were independently audited against official indexing services (CrossRef, PubMed, DBLP, Google Scholar, publisher portals):
- **Verification Coverage:** 100% of the 42 references are verified authentic academic works with accurate titles, authors, venues, years, volume/issue numbers, and DOIs.
- **Citation Parity:** Every reference in `references.bib` is cited in the text of `ARES_preprint.tex` via `\cite{...}`, and every in-text citation resolves to an authentic bibliography entry.
- **Zero Hallucinations:** No citations, author names, or volume/page numbers were fabricated or altered.

---

### 6. Summary of Ongoing Work

1. **Empirical Walk-Forward Execution:** Ingestion of full 2018--2025 raw historical data across the Galwan Valley, Taiwan Strait, and Myanmar conflicts to extract true empirical lead times, Brier scores, and precision-recall AUC curves.
2. **PostGIS Schema Migration:** Migrating the demonstrator SQLite database to PostgreSQL/PostGIS to support true `ST_Contains` spatial queries on regional shapefiles.
3. **Probability Calibration:** Fitting isotonic regression curves on historical training intervals to output Bayesian posterior probabilities $P(\text{Escalation} \mid X)$.
