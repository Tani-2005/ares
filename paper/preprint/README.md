# ARES: Conflict Escalation Early Warning System
## Elsevier `elsarticle` Research Preprint Repository

**Preprint Date:** October 2026  
**Document Class:** Elsevier `elsarticle.cls` (`\documentclass[preprint,12pt]{elsarticle}`)  
**Bibliography Style:** `elsarticle-num.bst` (IEEE-compatible numeric citation order)  

---

### Authors & Institutional Affiliation

1. **Shirin S. Hegde** — `1by23is198@bmsit.in`
2. **Sreshta Karthikeyan** — `1by23is215@bmsit.in`
3. **Tanya Deep** — `1by23is231@bmsit.in`

*Department of Information Science and Engineering, BMS Institute of Technology and Management, Bengaluru, Karnataka, India.*

> **Author & USN Conventions:**
> - Authors are listed in strict ascending numerical order of their university USN (`1by23is198` < `1by23is215` < `1by23is231`).
> - All USNs are formatted strictly in lowercase within institutional emails.
> - Author bylines exclude supervisory and student role designations in accordance with academic preprint conventions.

---

### Repository File Inventory

| File | Type | Description |
| :--- | :--- | :--- |
| [`ARES_preprint.tex`](ARES_preprint.tex) | LaTeX Source | Complete manuscript typeset in official Elsevier `elsarticle.cls` format. |
| [`ARES_preprint.pdf`](ARES_preprint.pdf) | Compiled Document | Publication-grade PDF compiled from `ARES_preprint.tex`. |
| [`references.bib`](references.bib) | BibTeX Database | 42 authentic, verified peer-reviewed citations with CrossRef/DOI metadata. |
| [`elsarticle.cls`](elsarticle.cls) | Class File | Official Elsevier LaTeX document class (preprint, 12pt). |
| [`elsarticle-num.bst`](elsarticle-num.bst) | Bibliography Style | Official Elsevier numbered bibliography style engine. |
| [`ARES_integrity_audit.md`](ARES_integrity_audit.md) | Integrity Audit | Comprehensive audit separating implemented software from prospective evaluation protocols. |
| [`README.md`](README.md) | Documentation | Compilation instructions, dependency guide, and template specifications. |

---

### Compilation Instructions

#### Method 1: Using Tectonic (Recommended, Self-Contained)
The project includes a self-contained modern XeTeX compiler (`tools/tectonic.exe`) that automatically handles package dependencies and multi-pass BibTeX resolution in a single execution:
```bash
./tools/tectonic.exe paper/preprint/ARES_preprint.tex
```

#### Method 2: Using Standard TeX Live / MiKTeX (`pdflatex` + `bibtex`)
To compile using standard command-line tools:
```bash
cd paper/preprint
pdflatex ARES_preprint.tex
bibtex ARES_preprint
pdflatex ARES_preprint.tex
pdflatex ARES_preprint.tex
```

#### Method 3: Uploading to Overleaf
1. Create a **New Project** $\rightarrow$ **Upload Project (ZIP)** on Overleaf.
2. Include:
   - `ARES_preprint.tex`
   - `references.bib`
   - `elsarticle.cls`
   - `elsarticle-num.bst`
3. Set the compiler to **pdfLaTeX** or **XeLaTeX** and set main document to `ARES_preprint.tex`.

---

### Section & Structure Map

The manuscript follows standard Elsevier flowing research paper layout:
1. **Frontmatter**: Title, Authors (with lowercase USN emails), Affiliation, Abstract (single paragraph), Keywords.
2. **Section 1: Introduction**: Precursor accumulation, 3 structural challenges, and human-in-the-loop operational boundary.
3. **Section 2: Related Work**: 5 domain literature clusters and **Table 1** (Comparative Positioning).
4. **Section 3: Research Gap and Contributions**: Nearest-neighbour analysis (ViEWS) and 4 core system contributions.
5. **Section 4: Research Questions and Objectives**: RQ1--RQ3 and engineering objectives O1--O5.
6. **Section 5: System Architecture**: Modular Monolith dataflow across 6 functional submodules.
7. **Section 6: Data Sources and Geographic Harmonization**: Ingestion of 12 OSINT data streams, canonical `Region_Key` zoning (Zone A theater, Zone B sphere), and **Table 2** (Data Sources & Constraints).
8. **Section 7: Feature Engineering and Risk Scoring**: Formulations for Event Acceleration, Tone Volatility, Protest Ratio, Economic Stress, Diplomatic Silence, Sigmoid Z-Score Fusion, and Isolation Forest Anomaly Detection.
9. **Section 8: Explainability and Human-in-the-Loop Decision Support**: Epistemic attribution vs. causality, and dynamic source URL evidence tracebacks.
10. **Section 9: Evaluation Protocol**: Leakage-free prospective backtesting protocol across 2020 Galwan, 2022 Taiwan, and 2021 Myanmar crises.
11. **Section 10: Results and Implementation Status**: **Table 3** (13-subsystem implementation audit).
12. **Section 11: Discussion**: Systems engineering pragmatic realities, latency handling, and narrative divergence.
13. **Section 12: Limitations, Ethics, and Responsible Use**: Media reporting bias, HITL governance, data privacy.
14. **Section 13: Conclusion and Future Work**: Technical summary and 3-phase research roadmap.
15. **References**: 42 numbered entries formatted via `elsarticle-num.bst`.
