# ARES Manuscript Changelog & Scientific Integrity Record

This document records all substantive revisions, methodological qualifications, and scientific integrity corrections made to the ARES research manuscript across versions.

---

## [Version 1.0.0-preprint] — October 2026

### 🔬 Scientific Integrity & Empirical Reporting
- **Removed Unverified Empirical Claims**: Eliminated placeholder backtest metrics from earlier informal drafts (which previously reported speculative numbers such as 78.4% recall, 82.1% precision, 11.6% FPR, and 7–21 days lead time without experimental execution logs).
- **Established Prospective Evaluation Protocol**: Authored a complete, formal, prospective experimental design in Section 9, specifying strict historical cutoff dates ($T_{\text{cutoff}} < T_{\text{peak}}$), chronological train/validation/test splits without temporal leakage, rare-event class weighting, and benchmark baselines (naïve persistence, moving average, logistic regression).
- **Explicit Results Status**: Formally declared in Section 10 that *no empirical predictive accuracy or lead-time claims are made in this version of the preprint*. The manuscript is positioned accurately as a foundational engineering, architectural, and data fusion framework.

### 📚 Literature Positioning & Nearest-Neighbour Synthesis
- **Identified Single Closest Prior Work**: Formally established **ViEWS (Political Violence Early-Warning System, Hegre et al., 2019)** as the nearest neighbour.
- **Formalized Research Gap Statement**: Articulated the precise one-sentence research boundary separating ARES from ViEWS, ICEWS-RF (Ward et al., 2013), and GDELT attention networks (Hossain et al., 2023).
- **Grounded Comparison Matrix**: Built an objective comparative positioning table grounded in 42 verified peer-reviewed publications, removing unsubstantiated characterizations of competing systems.
- **Honest Novelty Positioning**: Reframed ARES as a robust systems-engineering framework integrating existing techniques rather than claiming "unprecedented" algorithmic novelty.

### 📐 Mathematical & Methodological Formalization
- **Edge-Case & Denominator Auditing**: Verified zero-denominator safeguards for Event Acceleration ($A(t)$) and Protest-to-Violence Ratio ($R_{\text{pv}}$) using $\max(\cdot, 1)$.
- **Qualification of Feature Weights**: Explicitly clarified that feature weights ($w_k$) in the Sigmoid Z-Score Fusion Engine are **domain-informed heuristic parameters** derived from conflict literature (Mach et al., 2019; Hsiang et al., 2013), not empirically learned or calibrated values.
- **Distinction of Risk Index vs. Probability**: Clarified that the 0–100 composite risk score is a bounded multi-criteria decision-support index, NOT a calibrated Bayesian posterior probability $P(\text{Escalation} \mid X)$.
- **Temporal Alignment of Macroeconomics**: Documented the step-wise constant backward-fill mechanism used to align low-frequency quarterly economic data with high-frequency daily event/news streams.
- **Attribution vs. Causality**: Explicitly separated statistical feature contribution (correlation / tree splits) from counterfactual causal inference, cautioning analysts against conflating predictive correlation with root cause.

### 🏗️ Implementation Verification & Architecture
- **Implementation Status Audit**: Constructed a comprehensive component classification table separating *Implemented and Verified*, *Implemented but not Independently Verified*, *Designed/Specified*, and *Proposed Future Work*.
- **Clarified Database Implementation**: Documented that the current operational demonstrator utilizes SQLite (`master_data.db`) with relational country-zone mappings, while the full PostGIS polygon spatial-containment schema remains specified for enterprise deployment.
- **Documented Multi-Source Ingestion**: Verified live API integrations for GDELT 2.0 (Doc API & GKG Themes), World Bank REST API, IMF Datamapper API, UCDP GED, and ReliefWeb.

### 🛡️ Ethical Governance & Limitations
- **Decision-Support Boundary**: Formally restricted the operational boundary of ARES to non-autonomous human analyst decision support.
- **Biases Addressed**: Detailed explicit mitigation strategies for state propaganda narrative divergence, media reporting inequality, and linguistic representation boundaries.

---

## [Initial Working Drafts] — February–April 2026
- Initial project proposal, architecture draft, and student IEEE paper stub created at BMSIT&M.
- Contained preliminary mathematical sketches and placeholder backtesting sections intended for subsequent empirical populating.
