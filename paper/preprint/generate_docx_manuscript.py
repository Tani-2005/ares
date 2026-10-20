import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

def set_cell_background(cell, fill_hex):
    tcPr = cell._element.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._element.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def create_preprint_docx():
    doc = docx.Document()

    # Section Margins
    for section in doc.sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)

    # Base Normal Style
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Times New Roman'
    normal_style.font.size = Pt(10.5)
    normal_style.font.color.rgb = RGBColor(0x22, 0x22, 0x22)
    normal_style.paragraph_format.line_spacing = 1.15
    normal_style.paragraph_format.space_after = Pt(4)

    # Helper functions
    def add_title(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(4)
        run = p.add_run(text)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(18)
        run.font.bold = True
        run.font.color.rgb = RGBColor(0x1B, 0x36, 0x5D)
        return p

    def add_subtitle(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(12)
        run = p.add_run(text)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
        run.font.italic = True
        run.font.color.rgb = RGBColor(0x44, 0x44, 0x44)
        return p

    def add_sec_head(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(16)
        p.paragraph_format.space_after = Pt(5)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(13)
        run.font.bold = True
        run.font.color.rgb = RGBColor(0x1B, 0x36, 0x5D)
        return p

    def add_subsec_head(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(11)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(11)
        run.font.bold = True
        run.font.color.rgb = RGBColor(0x33, 0x33, 0x33)
        return p

    def add_p(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(4)
        run = p.add_run(text)
        return p

    def add_callout(title, bullets):
        tbl = doc.add_table(rows=1, cols=1)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell = tbl.cell(0, 0)
        set_cell_background(cell, "F0F4F8")
        set_cell_margins(cell, top=100, bottom=100, left=150, right=150)
        p0 = cell.paragraphs[0]
        p0.paragraph_format.space_after = Pt(4)
        r0 = p0.add_run(title)
        r0.font.bold = True
        r0.font.size = Pt(10.5)
        r0.font.color.rgb = RGBColor(0x1B, 0x36, 0x5D)
        for b_title, b_text in bullets:
            p = cell.add_paragraph(style='List Bullet')
            p.paragraph_format.space_after = Pt(2)
            rb = p.add_run(b_title)
            rb.font.bold = True
            rb.font.size = Pt(9.5)
            rt = p.add_run(b_text)
            rt.font.size = Pt(9.5)
        doc.add_paragraph().paragraph_format.space_after = Pt(4)

    # Document Header / Academic Banner
    p_inst = doc.add_paragraph()
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_inst.paragraph_format.space_after = Pt(2)
    r_inst = p_inst.add_run("BMS INSTITUTE OF TECHNOLOGY AND MANAGEMENT\n(An Autonomous Institute under VTU, Belagavi, Karnataka)\nDepartment of Information Science and Engineering")
    r_inst.font.name = 'Times New Roman'
    r_inst.font.size = Pt(9.5)
    r_inst.font.bold = True
    r_inst.font.color.rgb = RGBColor(0x1B, 0x36, 0x5D)

    add_title("ARES: An Explainable Multi-Source Data Fusion Framework for Conflict Escalation Early Warning")
    add_subtitle("A Living Preprint on Spatio-Temporal Ingestion, Feature Modeling, and Decision-Support Architecture")

    # Author Metadata Table
    table_auth = doc.add_table(rows=2, cols=3)
    table_auth.alignment = WD_TABLE_ALIGNMENT.CENTER
    table_auth.autofit = False

    authors = [
        ("Tanya Deep", "USN: 1BY23IS231", "System Dev & Visualization Lead"),
        ("Shirin S. Hegde", "USN: 1BY23IS198", "Data Engineering & Integration Lead"),
        ("Sreshta Karthikeyan", "USN: 1BY23IS215", "AI/ML Model Developer")
    ]

    for col_idx, (name, usn, role) in enumerate(authors):
        cell_top = table_auth.cell(0, col_idx)
        cell_bot = table_auth.cell(1, col_idx)
        p0 = cell_top.paragraphs[0]
        p0.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r0 = p0.add_run(f"{name}\n({usn})")
        r0.font.bold = True
        r0.font.size = Pt(10)
        p1 = cell_bot.paragraphs[0]
        p1.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r1 = p1.add_run(f"{role}\nDept. of ISE, BMSIT&M")
        r1.font.size = Pt(9)
        r1.font.italic = True
        set_cell_background(cell_top, "F4F6F9")
        set_cell_background(cell_bot, "F4F6F9")
        set_cell_margins(cell_top, top=80, bottom=40, left=80, right=80)
        set_cell_margins(cell_bot, top=40, bottom=80, left=80, right=80)

    p_guide = doc.add_paragraph()
    p_guide.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_guide.paragraph_format.space_before = Pt(8)
    p_guide.paragraph_format.space_after = Pt(12)
    rg = p_guide.add_run("Under the Guidance of: Prof. Sneha Sureddy, Assistant Professor, Dept. of ISE, BMSIT&M\nCorrespondence: tanya.deep@bmsit.res.in, snehasureddy@bmsit.in")
    rg.font.size = Pt(9.5)
    rg.font.bold = True

    # Abstract Callout Box
    add_callout(
        "ABSTRACT",
        [
            ("Research Problem: ", "Quantitative conflict forecasting has historically been dominated by retrospective event databases that record political violence after casualties and physical damage have already occurred, leaving policymakers and humanitarian agencies in a posture of reactive response."),
            ("Limitation Addressed: ", "While recent deep learning and graph neural network models predict isolated violent incidents, they function as uninterpretable black boxes and fail to synthesize multi-domain precursors (narrative tone, economic decay, diplomatic silence)."),
            ("Proposed Framework: ", "ARES (Advanced Reconnaissance & Escalation System) is an explainable multi-source data fusion framework engineered for continuous geopolitical escalation early warning. It unifies physical conflict events (ACLED, UCDP), real-time news sentiment volatility (GDELT), macroeconomic stress gradients (World Bank, IMF), and diplomatic signals (UN records, GSDB) through a standardized Region_Key."),
            ("Current Status & Contribution: ", "The complete modular monolith pipeline, parallel ingestion engine, spatial-temporal feature store, Sigmoid Z-Score fusion algorithm (0-100 risk index), unsupervised IsolationForest anomaly detector, and interactive Streamlit decision-support dashboard are implemented and verified. In accordance with scientific integrity standards, no empirical forecasting claims or lead times are asserted prior to execution of the formal backtest protocol."),
            ("Keywords: ", "Conflict Escalation, Early-Warning Systems, Multi-Source Data Fusion, Explainable AI, Spatio-Temporal Modeling, Decision Support Systems, GDELT, ACLED.")
        ]
    )

    # Policy Significance Callout
    add_callout(
        "POLICY & EARLY-WARNING SIGNIFICANCE BOX",
        [
            ("What is already known on this topic: ", "Political violence forecasting systems (e.g., ViEWS, ICEWS) demonstrate that historical conflict events and structural covariates carry predictive signal for monthly violence onset at national and grid-cell levels."),
            ("What this study adds: ", "A reproducible engineering framework that fuses high-frequency media sentiment volatility, kinetic event acceleration, low-frequency macroeconomic distress, and diplomatic signaling under a unified Region_Key lookup."),
            ("Decision-Support Grounding: ", "An explainable-by-design interface attaching local factor breakdowns and verifiable source URLs to every risk tier, backed by a leakage-free prospective historical backtesting protocol.")
        ]
    )

    # SECTION 1
    add_sec_head("1. Introduction & Motivation")
    add_p(
        "Armed conflicts, border skirmishes, and civil unrest rarely emerge as instantaneous, unheralded shocks. Almost universally, kinetic escalation is preceded by an observable, progressive accumulation of precursor signals: localized protest escalation, sharp negative shifts in media tone, hyperinflationary economic distress, and deteriorating diplomatic engagement [1]-[5]. Over the past decade, the democratization of open-source intelligence (OSINT) has produced vast volumes of machine-readable geopolitical data, ranging from sub-national armed clash logs (ACLED [7], UCDP [10]) and global news sentiment feeds (GDELT [8]) to multilateral economic indicators (World Bank, IMF [35]-[40])."
    )
    add_p(
        "However, existing conflict-monitoring infrastructure suffers from a fundamental operational limitation: it remains overwhelmingly reactive. Systems catalog violent events after they occur, functioning as historical documentation registries rather than predictive sentinels. When security analysts and humanitarian planners rely exclusively on retrospective clash counts, preventative diplomacy and risk mitigation cannot be mobilized until violence is already underway."
    )
    add_p(
        "To transition from retrospective documentation to proactive early warning, computational social science has increasingly applied statistical and machine learning models to conflict forecasting. Yet, existing computational forecasting approaches face three interrelated challenges:"
    )
    
    challenges = [
        ("1) Temporal Horizon Mismatch: ", "Leading predictive systems typically forecast binary conflict onset over long monthly or yearly horizons at coarse geographic levels (e.g., country-month or 0.5° × 0.5° PRIO-grid cells [1]-[3]). They do not track the continuous, dynamic daily transitions from baseline stability to diplomatic friction, narrative polarization, and kinetic crisis."),
        ("2) Interpretability Crisis in Decision Support: ", "Recent deep temporal learning and dynamic graph representations (e.g., Temporal Graph Networks [13], EvolveGCN [14], deep attention mechanisms [19]) achieve high statistical fit but function as opaque black boxes. In high-stakes geopolitical analysis, a risk alert generated by an uninterpretable latent state cannot be validated, defended, or acted upon by human analysts. If a system cannot explain which specific factors triggered an alert and which verified source records substantiate it, it will inevitably be discounted by decision-makers."),
        ("3) Spatial-Temporal Data Heterogeneity: ", "Escalation drivers span wildly incompatible scales. Kinetic clashes occur at discrete latitude/longitude coordinates on specific hours; news tone fluctuates across millions of unstructured articles daily; and macroeconomic stress indicators (GDP growth, CPI inflation, unemployment) are reported quarterly or annually at national aggregations. Harmonizing these disparate streams into a coherent analytical matrix without introducing severe aggregation noise remains an unsolved engineering challenge.")
    ]
    for b_title, b_desc in challenges:
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_after = Pt(2)
        rb = p.add_run(b_title)
        rb.font.bold = True
        p.add_run(b_desc)

    add_subsec_head("Operational Boundary: Human-in-the-Loop Decision Support")
    add_p(
        "ARES is explicitly designed as a human-in-the-loop decision-support framework. It does not execute autonomous interventions, weapons dispatch, or automated policy enforcement. Its bounded objective is to ingest heterogeneous open data, compute transparent risk scores, detect statistical multi-variable anomalies, and present human analysts with an interpretable, source-traceable operational picture."
    )

    # SECTION 2
    add_sec_head("2. Related Work & Comparative Positioning")
    add_p(
        "Early quantitative conflict forecasting relied heavily on low-resolution regression frameworks using macro-structural covariates (GDP per capita, regime type, total population). A seminal breakthrough was achieved by Hegre et al. with the ViEWS (Political Violence Early-Warning System) framework [1]-[3], which established an ensemble machine learning architecture forecasting monthly conflict probabilities at the country and subnational PRIO-grid level using UCDP data. In parallel, Ward et al. [4] demonstrated that Random Forest classifiers trained on subnational event data from the Integrated Crisis Early Warning System (ICEWS [9]) could forecast domestic political instability with higher predictive power than classical logit specifications. Brandt et al. [5] developed Bayesian spatio-temporal Poisson models to capture regional spillover dynamics, while Muchlinski et al. [6] systematically evaluated machine learning against logistic regression on highly imbalanced civil war onset datasets, demonstrating the superior capacity of tree-based ensembles to navigate rare-event class distributions without succumbing to majority-class collapse. The foundational grounding for these empirical models rests on standardized event repositories, notably ACLED (Raleigh et al. [7]), GDELT (Leetaru & Schrodt [8]), ICEWS (Boschee et al. [9]), and UCDP GED (Sundberg & Melander [10]; Gleditsch et al. [11]; Chojnacki et al. [12])."
    )
    add_p(
        "To capture dynamic interactions among geopolitical actors, recent studies have embraced graph neural networks (GNNs) and temporal knowledge graphs. Rossi et al. [13] introduced Temporal Graph Networks (TGNs) for continuous-time dynamic relational graphs, while Pareja et al. [14] proposed EvolveGCN to adapt graph convolutional parameters across time steps using recurrent architectures. Trivedi et al. [15], [16] formulated dynamic relational representations via DyRep and Know-Evolve. In specialized security domains, Campedelli et al. [18] modeled terrorist target selection using meta-graphs, and Hossain et al. [19] deployed multi-head attention networks across GDELT event streams to detect early precursor signals of geopolitical friction. While these deep relational architectures excel at modeling latent topological actor shifts, they impose severe opacity: attention weights and node embeddings cannot be straightforwardly translated into operational evidence trails for defense analysts."
    )
    add_p(
        "A substantial macroeconomic and political science literature demonstrates that economic shocks and environmental disruptions serve as baseline structural drivers of conflict. Synthesizing cross-disciplinary expert consensus, Mach et al. [35] established climate and environmental volatility as measurable risk multipliers for organized violence. Hsiang et al. [36] and Burke et al. [37] demonstrated non-linear relationships between climatic anomalies, macroeconomic productivity loss, and interpersonal/intergroup conflict. Earlier empirical work by Miguel et al. [38], Collier & Hoeffler [39], and Fearon & Laitin [40] proved that negative income shocks, soaring inflation, and rapid unemployment spikes severely lower the opportunity cost of rebellion and civil unrest, justifying the integration of macroeconomic stress indicators alongside kinetic event data."
    )
    add_p(
        "Predicting future risk trajectories over rolling horizons builds upon multivariate time-series modeling. Lim et al. [31] introduced the Temporal Fusion Transformer (TFT), combining recurrent layers with self-attention to provide interpretable multi-horizon quantile forecasts. Salinas et al. [32] formulated DeepAR, an autoregressive recurrent network producing probabilistic forecasts over volatile, sparse event counts. Zerveas et al. [33] demonstrated self-supervised transformer representations for multivariate time series. For unsupervised anomaly detection in non-linear feature spaces without labeled outlier annotations, Liu et al. [34] developed the Isolation Forest algorithm, isolating rare multidimensional anomalies through recursive random partitioning."
    )
    add_p(
        "In high-stakes analytical settings, predictive systems must satisfy rigorous interpretability constraints. Theoretical frameworks by Schölkopf et al. [41] emphasize that machine learning models deployed in non-stationary environments must learn causal representations rather than superficial observational correlations to avoid catastrophic failure under distribution shifts. Athey & Imbens [42] outlined rigorous methodologies for estimating heterogeneous treatment effects and decomposing complex machine learning outputs into actionable, interpretable drivers. These principles underpin ARES's architectural mandate that every alert must provide localized factor attributions and verifiable source-level evidence trails."
    )

    # TABLE 1: COMPARATIVE POSITIONING
    add_subsec_head("Comparative Positioning Against State-of-the-Art Platforms")
    add_p("Table 1 provides an objective, grounded comparison between ARES and leading computational conflict forecasting platforms.")

    t1 = doc.add_table(rows=5, cols=5)
    t1.alignment = WD_TABLE_ALIGNMENT.CENTER
    t1.autofit = False

    headers_t1 = ["Platform / Work", "Core Modeling Methodology", "Data Integration Scope", "Spatial & Temporal Resolution", "Explainability & Traceability"]
    for i, h in enumerate(headers_t1):
        cell = t1.cell(0, i)
        cell.text = h
        set_cell_background(cell, "1B365D")
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        p.runs[0].font.bold = True
        p.runs[0].font.size = Pt(8.5)

    data_t1 = [
        ("ViEWS\n(Hegre et al. [1]-[3])", "Ensemble ML (Logit, Random Forest, Hurdle models)", "UCDP conflict events + structural geographic/demographic covariates", "0.5° × 0.5° PRIO-grid & country-month (1-36 mo horizon)", "Low to Med: Global feature importances; country-level risk profiles; no local live tracebacks."),
        ("ICEWS-RF\n(Ward et al. [4])", "Random Forest classifiers", "ICEWS diplomatic and crisis event logs", "Subnational administrative units; monthly intervals", "Low: Global Gini feature importance; no local per-prediction attribution; no source URLs."),
        ("GDELT-Attention\n(Hossain et al. [19])", "Deep Attention Neural Networks", "GDELT media events and localized tone streams", "National level; multi-day event sequence horizons", "Low: Latent attention weights unmapped to operational evidence; opaque neural activations."),
        ("ARES\n(This Project)", "Domain-Calibrated Sigmoid Z-Score Fusion + Isolation Forest", "4 Domains: Conflict Events + News Tone + Macroeconomics + Diplomatic", "Regional/National Region_Key zones; daily rolling windows (7d, 14d, 30d)", "High: Mandatory local factor attribution breakdown + direct raw-source URL tracebacks.")
    ]

    for row_idx, rdata in enumerate(data_t1):
        row_cells = t1.rows[row_idx + 1].cells
        bg_col = "EAF2F8" if row_idx == 3 else ("F9FAFB" if row_idx % 2 == 0 else "FFFFFF")
        for col_idx, val in enumerate(rdata):
            row_cells[col_idx].text = val
            set_cell_background(row_cells[col_idx], bg_col)
            set_cell_margins(row_cells[col_idx], top=50, bottom=50, left=70, right=70)
            p = row_cells[col_idx].paragraphs[0]
            p.runs[0].font.size = Pt(8)
            if row_idx == 3:
                p.runs[0].font.bold = True

    # SECTION 3
    add_sec_head("3. Research Gap & Novelty Assessment")
    add_p(
        "Nearest-Neighbour Analysis: The single closest prior system to ARES is ViEWS (Hegre et al., 2019) [1]. Both systems seek to provide subnational early warning of political violence using machine learning and open data. However, ViEWS is optimized for medium- to long-range structural forecasting (months to years) using monthly calendar aggregations and static structural covariates."
    )
    add_p(
        "The Research Gap Statement: The precise scientific gap addressed by ARES is formulated in a single sentence:"
    )
    
    p_gap = doc.add_paragraph()
    p_gap.paragraph_format.left_indent = Inches(0.25)
    p_gap.paragraph_format.right_indent = Inches(0.25)
    p_gap.paragraph_format.space_before = Pt(6)
    p_gap.paragraph_format.space_after = Pt(6)
    r_gap = p_gap.add_run(
        "“While established conflict early-warning frameworks such as ViEWS demonstrate the viability of ensemble statistical forecasting over monthly grid-cell event data, they operate primarily on retrospective monthly event logs with global model-level feature importances; ARES contributes an explainable, multi-source data fusion engineering framework that harmonizes near-real-time media tone volatility, physical conflict events, macroeconomic stress gradients, and diplomatic signaling into an interpretable daily risk score with mandatory per-alert factor attribution and raw source-evidence traceability.”"
    )
    r_gap.font.bold = True
    r_gap.font.italic = True
    r_gap.font.color.rgb = RGBColor(0x1B, 0x36, 0x5D)

    add_p(
        "Bounded Novelty Claim: ARES does not claim the creation of a fundamentally new machine learning algorithm. Rather, its scientific and technical contribution is an engineering and data-fusion framework that: (1) reconciles radically disparate spatial, temporal, and semantic data streams into a unified spatio-temporal representation (Region_Key); (2) enforces strict mathematical explainability at the decision boundary, preventing black-box opacity in sensitive defense and humanitarian contexts; and (3) provides an end-to-end, reproducible software architecture linking live OSINT ingestion to an analyst-facing decision-support dashboard."
    )

    # SECTION 4
    add_sec_head("4. Research Questions & Design Objectives")
    add_p("This research is organized around three fundamental research questions:")
    
    rqs = [
        ("RQ1 (Spatio-Temporal Harmonization): ", "Can heterogeneous geopolitical data streams operating across disparate spatial formats (coordinate points, national ISO codes) and temporal frequencies (daily news streams, quarterly macroeconomic indicators) be harmonized into a standardized feature matrix without introducing critical temporal leakage or destructive aggregation artifacts?"),
        ("RQ2 (Explainability & Decision-Support Verification): ", "How can multi-criteria risk scoring be formulated such that high-dimensional statistical anomaly signals are mapped directly to human-interpretable factor attributions and verifiable open-source URLs?"),
        ("RQ3 (Prospective Lead Time & False-Alarm Trade-Offs): ", "Under rigorous retrospective historical backtesting with pre-peak data cutoffs (T_cutoff < T_peak), does a multi-source fusion model achieve positive early-warning lead times (7–21 days) while suppressing false alarm rates (<15%) during peacetime baselines?")
    ]
    for b_title, b_desc in rqs:
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_after = Pt(2)
        rb = p.add_run(b_title)
        rb.font.bold = True
        p.add_run(b_desc)

    # SECTION 5
    add_sec_head("5. ARES System Architecture")
    add_p(
        "ARES is engineered following the Modular Monolith architectural pattern. All computational pipelines execute within a unified software environment, eliminating the network latency, service discovery complexity, and distributed state overhead of microservices while enforcing strict logical separation of concerns across internal modules:"
    )
    
    arch_modules = [
        ("/ingestion: ", "Coordinates asynchronous external API requests via Python asyncio, aiohttp, and requests. Manages HTTP rate limits, exponential backoff (base 2s, 3 retries), and payload hashing to prevent redundant database writes."),
        ("/preprocessing: ", "Sanitizes raw strings, normalizes ISO country entities into canonical Region_Key identifiers, imputes missing fields via historical forward-fill, and clips numeric outliers."),
        ("/storage: ", "Provides an abstraction layer over local relational storage (SQLite master_data.db in demonstrator; PostgreSQL + PostGIS schema specified for production). Fact tables carry composite indices on (region_key, event_date)."),
        ("/features: ", "Executes rolling window transformations (W ∈ {7, 14, 30} days) generating mathematical features for event acceleration, tone volatility, protest transition, and economic distress."),
        ("/model: ", "Computes the composite Sigmoid Z-Score risk score, executes IsolationForest anomaly partitioning, and derives feature attribution rankings."),
        ("/frontend & /api: ", "Renders an interactive multi-view Streamlit dashboard (artifacts/ares-dashboard/app.py) providing mission status cards, regional heatmaps, interactive Plotly trendlines, and source evidence feeds, mirrored by an Express 5 TypeScript API monorepo.")
    ]
    for b_title, b_desc in arch_modules:
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_after = Pt(2)
        rb = p.add_run(b_title)
        rb.font.bold = True
        p.add_run(b_desc)

    # SECTION 6
    add_sec_head("6. Data Sources & Geographic Harmonization")
    add_p(
        "ARES integrates 12 heterogeneous geopolitical, economic, and diplomatic data sources, reconciling point-coordinates, textual sentiment, and macroeconomic indicators."
    )

    # TABLE 2: DATA SOURCES
    add_subsec_head("Multi-Source Ingestion Catalog & Constraints")
    t2 = doc.add_table(rows=13, cols=5)
    t2.alignment = WD_TABLE_ALIGNMENT.CENTER
    t2.autofit = False

    headers_t2 = ["Source Name", "Domain", "Ingestion Modality", "Reporting Cadence", "Licensing & Terms of Use"]
    for i, h in enumerate(headers_t2):
        cell = t2.cell(0, i)
        cell.text = h
        set_cell_background(cell, "1B365D")
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        p.runs[0].font.bold = True
        p.runs[0].font.size = Pt(8.5)

    sources_data = [
        ("ACLED", "Kinetic Conflict", "Structured CSV / API", "Weekly / Daily", "Academic non-commercial; mandatory attribution."),
        ("GDELT 2.0", "Narrative Tone / Events", "Live JSON REST API", "15-minute stream", "Open access / Public domain; attribution requested."),
        ("UCDP GED", "Kinetic Conflict", "REST API / Static", "Annual / Monthly", "CC BY 4.0 open academic license."),
        ("ICEWS", "Crisis Events", "Harvard Dataverse", "Historical", "Open research data; Harvard Dataverse terms."),
        ("World Bank API", "Macroeconomics", "Live REST API", "Annual / Quarterly", "CC BY 4.0 Open Data."),
        ("IMF Datamapper", "Macroeconomics", "Live REST API", "Bi-annual (WEO)", "Open data with citation."),
        ("ReliefWeb", "Humanitarian Crisis", "Live REST API", "Daily", "CC BY 4.0 Open Humanitarian Data."),
        ("UN Sanctions", "Diplomatic", "Static Database", "Semi-annual", "UN public domain records."),
        ("UNGA Voting", "Diplomatic", "Static CSV", "Annual", "Open academic dataset."),
        ("SIPRI", "Arms Transfers", "Static Database", "Annual", "SIPRI open access policy; citation required."),
        ("GSDB", "Sanctions", "Static Database", "Annual", "Global Sanctions Database; academic open access."),
        ("Exchange Rates", "Currency Volatility", "Live REST API", "Daily", "Open financial exchange APIs.")
    ]

    for row_idx, rdata in enumerate(sources_data):
        row_cells = t2.rows[row_idx + 1].cells
        bg_col = "F9FAFB" if row_idx % 2 == 0 else "FFFFFF"
        for col_idx, val in enumerate(rdata):
            row_cells[col_idx].text = val
            set_cell_background(row_cells[col_idx], bg_col)
            set_cell_margins(row_cells[col_idx], top=40, bottom=40, left=60, right=60)
            p = row_cells[col_idx].paragraphs[0]
            p.runs[0].font.size = Pt(8)

    add_subsec_head("Geographic Harmonization via Canonical Region_Key")
    add_p(
        "To resolve spatial incompatibility between point-coordinates (lat/long) and national/regional reporting, ARES implements a canonical Region_Key schema. Two strategic zones are enforced: Zone A (The Conflict Theater — 16 core Indo-Pacific nations monitored at high resolution for kinetic and narrative shifts) and Zone B (The Influence Sphere — major external powers monitored for distal causal policy shifts, sanctions, and arms deals). Point coordinates are resolved to bounding polygons during ingestion, while unstructured text references are normalized to standardized atomic keys (e.g., ZoneA_IND, ZoneA_CHN)."
    )

    add_subsec_head("Temporal Resolution Alignment")
    add_p(
        "To synchronize high-frequency daily event/sentiment data with quarterly macroeconomic statistics, ARES employs a step-wise constant backward-fill (carry-forward) strategy. Macroeconomic indicators (GDP, CPI, Unemployment) establish a static structural baseline vulnerability score for a region across a 90-day calendar quarter. High-frequency daily event counts and sentiment shocks are then computed as dynamic deviations over this structural baseline."
    )

    # SECTION 7
    add_sec_head("7. Feature Engineering & Mathematical Risk Modeling")
    add_p("ARES extracts 5 primary rolling features per region over lookback windows W ∈ {7, 14, 30} days:")

    formulas = [
        ("1) Event Acceleration (WoW Delta):",
         "A(t) = [ E_W(t) - E_W(t - W) ] / max(E_W(t - W), 1)",
         "Captures surges in kinetic frequency relative to historical baselines. Denominator bounded by max(·, 1) to eliminate division-by-zero errors when historical baseline is zero."),
        
        ("2) Sentiment Volatility (14d Rolling StdDev):",
         "σ_tone = sqrt( [1 / max(N - 1, 1)] * ∑_{i=1}^N (Tone_i - Tone_avg)^2 )",
         "Quantifies narrative polarization and media volatility over N news articles. Defaults to 0.0 for N ≤ 1."),
        
        ("3) Protest-to-Violence Transition Ratio:",
         "R_pv = Count(Protests) / max(Count(Protests) + Count(Violent Events), 1)",
         "Tracks the structural transition from peaceful civil demonstration (R_pv → 1) to kinetic clash (R_pv → 0). The inverted term (1 - R_pv) acts as the escalation penalty."),
        
        ("4) Macroeconomic Stress Gradient:",
         "S_econ = [1 / ∑ α_j] * [ α1·clamp((ΔCPI - 3.0)/15.0, 0, 1) + α2·clamp((2.0 - ΔGDP)/8.0, 0, 1) + α3·clamp((Unemp - 5.0)/15.0, 0, 1) ]",
         "Normalized index S_econ ∈ [0, 1] using literature-informed elasticities (α1=0.40, α2=0.35, α3=0.25) derived from Mach et al. [35] and Miguel et al. [38]."),
        
        ("5) Diplomatic Silence Duration:",
         "D_silence(t) = min( t - t_last_diplo, W_max )",
         "Counts elapsed calendar days since the last recorded bilateral diplomatic summit or treaty interaction.")
    ]

    for f_title, f_eq, f_desc in formulas:
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.2)
        p.paragraph_format.space_after = Pt(2)
        r1 = p.add_run(f"{f_title}\n")
        r1.font.bold = True
        r2 = p.add_run(f"    {f_eq}\n")
        r2.font.bold = True
        r2.font.italic = True
        r2.font.color.rgb = RGBColor(0x1B, 0x36, 0x5D)
        r3 = p.add_run(f"    {f_desc}")
        r3.font.size = Pt(9.5)

    add_subsec_head("Mathematical Sigmoid Z-Score Fusion Engine")
    add_p(
        "Features are standardized across regional cohort baselines into Z-scores (Z_k = (F_k - μ_k)/σ_k, with σ_k=0 yielding Z_k=0) and transformed via a domain-weighted logistic sigmoid:"
    )

    p_sig = doc.add_paragraph()
    p_sig.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sig.paragraph_format.space_before = Pt(6)
    p_sig.paragraph_format.space_after = Pt(6)
    rsig = p_sig.add_run("Risk_Score = 100 / ( 1 + exp( -∑_{k=1}^K w_k · Z_k ) )")
    rsig.font.bold = True
    rsig.font.size = Pt(11)
    rsig.font.color.rgb = RGBColor(0x1B, 0x36, 0x5D)

    add_p(
        "Calibrated Heuristic Feature Weights: Military Clash Count (w=0.30), Event Acceleration (w=0.20), Sentiment Volatility (w=0.15), Negative Tone (w=0.15), Diplomatic Silence (w=0.10), Macroeconomic Stress (w=0.10). Operational risk tiers: Green (0–32, Baseline), Amber (33–65, Elevated Tension), Red (66–100, Critical Escalation)."
    )
    add_p(
        "Methodological Qualification: The resulting Risk_Score is an uncalibrated multi-criteria decision-support index, NOT a calibrated Bayesian posterior probability P(Escalation | X). The weights w_k represent domain-informed relative importances rather than maximum-likelihood parameters."
    )

    add_subsec_head("Unsupervised IsolationForest Anomaly Detection")
    add_p(
        "To flag non-linear statistical anomalies without requiring labeled historical anomaly datasets, ARES applies an IsolationForest model (sklearn.ensemble.IsolationForest [34]) fitted on feature vectors X ∈ ℝ⁵ (contamination=0.10, random_state=42), returning anomaly flags (is_anomaly = True) for top 10% outlier region-window combinations."
    )

    # SECTION 8
    add_sec_head("8. Explainability & Human-in-the-Loop Decision Support")
    add_p(
        "Distinction Between Feature Attribution and Causal Explanation: A critical failure of modern machine learning applications in defense intelligence is the conflation of predictive feature attribution with causal explanation. When an algorithm indicates that Event Acceleration accounts for 58% of an elevated risk score, this represents a statistical decomposition of the linear combination ∑ w_k Z_k; it does not prove that event acceleration caused the geopolitical crisis. ARES enforces strict epistemic humility: feature attributions are labeled as 'Contributing Observed Indicators', and counter-evidence (cooperative summits, de-escalation statements) is presented to prevent confirmation bias."
    )
    add_p(
        "Direct Source Provenance: Every computed feature points back to database primary keys and external source URLs. When an analyst clicks an Amber or Red alert card, the dashboard renders a Source Evidence Feed detailing the exact headlines, timestamps, and URLs of the GDELT news articles and ACLED incident logs that drove the score, enabling human verification in under two minutes."
    )

    # SECTION 9
    add_sec_head("9. Prospective Evaluation Protocol")
    add_p(
        "In accordance with scientific integrity standards, because empirical historical backtesting experiments are currently in-progress, this section outlines the formal evaluation protocol designed to validate ARES against historical crisis benchmarks without temporal information leakage."
    )
    
    eval_steps = [
        ("Benchmark Cases: ", "Three documented Indo-Pacific crisis sequences: (1) 2020 Galwan Valley Border Standoff (India-China); (2) August 2022 Taiwan Strait Military Exercises; (3) 2021 Myanmar Civil Conflict."),
        ("Temporal Cutoff Safeguards (T_cutoff): ", "For any crisis peak at date T_peak, the model is strictly restricted to data up to T_cutoff = T_peak - Δt (Δt ∈ {7, 14, 21, 28} days). All normalization parameters and imputation statistics are fit strictly on pre-cutoff historical data to prevent future information leakage."),
        ("Chronological Splits: ", "Chronological partitioning (2018-2021 baseline calibration, 2022-2025 prospective evaluation). Random shuffling is strictly prohibited."),
        ("Comparative Baselines: ", "Naïve Persistence Baseline, Historical Rolling Mean Baseline, Univariate ARIMA, and Unregularized Logistic Regression."),
        ("Target Metrics: ", "Recall on High-Impact Events (Target ≥ 75%); Precision on High-Risk Alerts (Target ≥ 80%); False Positive Rate (Target < 15%); Early-Warning Lead Time τ_lead = T_peak - T_first_Red_alert (Target: 7 to 21 days); Brier Calibration Score; and Feature Ablation AUC drops.")
    ]
    for b_title, b_desc in eval_steps:
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_after = Pt(2)
        rb = p.add_run(b_title)
        rb.font.bold = True
        p.add_run(b_desc)

    # SECTION 10
    add_sec_head("10. Results & Implementation Status Audit")
    add_p(
        "In strict adherence to scientific integrity guidelines, no empirical predictive accuracy, lead times, or calibrated probability curves are reported as completed findings in this manuscript. The current contribution represents a verified, functional software framework and prospective experimental design."
    )

    # TABLE 3: IMPLEMENTATION STATUS
    add_subsec_head("Comprehensive Codebase Implementation Audit")
    t3 = doc.add_table(rows=14, cols=4)
    t3.alignment = WD_TABLE_ALIGNMENT.CENTER
    t3.autofit = False

    headers_t3 = ["Component / Subsystem", "Current Status", "Verification Location", "Technical Scope & Limitations"]
    for i, h in enumerate(headers_t3):
        cell = t3.cell(0, i)
        cell.text = h
        set_cell_background(cell, "1B365D")
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        p.runs[0].font.bold = True
        p.runs[0].font.size = Pt(8.5)

    status_data = [
        ("Live Ingestion Engine", "Implemented & Verified", "src/live_data.py", "Active REST fetchers for GDELT 2.0, World Bank, IMF, UCDP, ReliefWeb."),
        ("Static Baseline Ingestion", "Implemented & Verified", "src/static_data_generator.py", "Historical generators for ACLED, ICEWS, SIPRI, UN Sanctions (~10k records)."),
        ("Database Persistence Layer", "Implemented & Verified", "src/database.py", "SQLite (master_data.db) operational; PostGIS spatial schema specified."),
        ("Feature Engineering Pipeline", "Implemented & Verified", "src/feature_engineering.py", "Verified computation of acceleration, volatility, protest ratio, economic stress."),
        ("Sigmoid Z-Score Fusion Engine", "Implemented & Verified", "src/feature_engineering.py", "Continuous 0-100 risk scoring with domain-informed heuristic weights."),
        ("Unsupervised Anomaly Detector", "Implemented & Verified", "src/feature_engineering.py", "Operational IsolationForest (contamination=0.10) flagging outliers."),
        ("Analyst Decision Dashboard", "Implemented & Verified", "app.py", "Functional 5-page Streamlit web app on port 8000 with interactive Plotly views."),
        ("Source Evidence Traceability", "Implemented & Verified", "app.py", "Dynamic URL traceback linking risk scores to raw GDELT and ACLED records."),
        ("Supervised Classifier Head", "Designed / Specified", "SRS §3.4; Arch §3.2", "RandomForest / XGBoost classifiers specified; currently using Sigmoid Fusion."),
        ("Deep NLP Transformer Head", "Designed / Specified", "SRS §3.4; Tech Stack", "Fine-tuned DistilBERT head specified; currently uses GDELT Tone / Goldstein."),
        ("Full PostGIS Polygon Joins", "Designed / Specified", "Architecture Doc §2.1", "ST_Contains spatial queries specified; demonstrator uses table lookups."),
        ("Enterprise TypeScript Monorepo", "Partially Implemented", "artifacts/api-server/, lib/", "Express 5 REST API & Drizzle schemas created; operates alongside Python."),
        ("Historical Backtesting Execution", "Protocol Formalized", "Section 9 of Manuscript", "Full experimental protocol formalized; empirical execution ongoing.")
    ]

    for row_idx, rdata in enumerate(status_data):
        row_cells = t3.rows[row_idx + 1].cells
        bg_col = "F9FAFB" if row_idx % 2 == 0 else "FFFFFF"
        for col_idx, val in enumerate(rdata):
            row_cells[col_idx].text = val
            set_cell_background(row_cells[col_idx], bg_col)
            set_cell_margins(row_cells[col_idx], top=40, bottom=40, left=60, right=60)
            p = row_cells[col_idx].paragraphs[0]
            p.runs[0].font.size = Pt(8)

    # SECTION 11
    add_sec_head("11. Discussion")
    add_p(
        "Systems Engineering in Geopolitical Early Warning: In computational social science, published models frequently fail in deployment because they ignore raw data ingestion failures, API rate limits, coordinate mismatches, and analyst cognitive bandwidth. By delivering an open, modular framework connecting live APIs to an explainable scoring pipeline and interactive dashboard, ARES bridges the gap between theoretical modeling and operational intelligence."
    )
    add_p(
        "Handling Reporting Latency & Propaganda: Official conflict logs (ACLED, UCDP) operate on weekly or monthly curation cycles, while GDELT updates every 15 minutes. ARES uses media tone volatility as a high-frequency canary signal while relying on curated event databases for baseline ground-truth. To counter state media manipulation, ARES computes Narrative Divergence—measuring statistical variance between domestic state media reporting and international independent wire services."
    )

    # SECTION 12
    add_sec_head("12. Limitations, Ethics & Responsible AI Governance")
    add_p(
        "Bias Mitigation: (1) Media Coverage Bias (The CNN Effect): Open news data systematically over-reports urban, digitally connected centers while under-reporting telecommunications-constrained rural zones. ARES explicitly bounds confidence in low-density zones. (2) Linguistic Representation: Western corpora bias sentiment parsing; expanding multi-lingual models is a future priority. (3) False Alarms vs. Missed Crises: The prospective evaluation protocol is specifically designed to balance sensitivity and false-alarm suppression."
    )
    add_p(
        "Human-in-the-Loop Governance: ARES operates strictly under a non-autonomous governance model. Under no circumstances should automated early-warning scores trigger pre-emptive military action, economic sanctions, or coercive interventions without qualitative human intelligence verification."
    )
    add_p(
        "Privacy & Licensing: No PII is collected or tracked. News and social text are parsed strictly for aggregate sentiment. All datasets are utilized strictly under open-access, academic, and non-commercial terms."
    )

    # SECTION 13
    add_sec_head("13. Conclusion & Future Research Roadmap")
    add_p(
        "ARES demonstrates the feasibility of building an explainable, multi-source conflict early-warning framework on open-source foundations. By harmonizing kinetic events, media sentiment, macroeconomic stress, and diplomatic signaling through a canonical Region_Key, ARES advances conflict monitoring from reactive event cataloguing toward proactive early warning."
    )
    add_p(
        "Future Research Roadmap: (1) Executing the formal prospective backtesting protocol across documented Indo-Pacific crises (2020 Galwan, 2022 Taiwan, 2021 Myanmar); (2) Empirical probability calibration via Platt scaling / Isotonic Regression to output formal Bayesian posterior probabilities P(Escalation | X); and (3) Hybrid integration of Temporal Graph Networks (TGNs) for transnational actor-alliance dynamics."
    )

    # REFERENCES
    add_sec_head("References (42 Landmark Research Publications)")
    
    refs = [
        "[1] H. Hegre et al., 'ViEWS: A political violence early-warning system,' Journal of Peace Research, vol. 56, no. 2, pp. 155-174, 2019.",
        "[2] H. Hegre et al., 'Forecasting civil conflict along subnational lines,' Journal of Peace Research, vol. 55, no. 2, pp. 207-221, 2018.",
        "[3] H. Hegre et al., 'Predicting armed conflict, 2010-2050,' International Studies Quarterly, vol. 63, no. 1, pp. 135-147, 2019.",
        "[4] M. D. Ward et al., 'Predicting political instability using machine learning: An assessment of the ICEWS project,' International Studies Review, vol. 15, no. 4, pp. 521-538, 2013.",
        "[5] P. T. Brandt et al., 'Forecasting political conflict in space and time,' Journal of Conflict Resolution, vol. 60, no. 5, pp. 921-948, 2016.",
        "[6] D. Muchlinski et al., 'Comparing random forest with logistic regression for predicting class-imbalanced civil war onset data,' Political Analysis, vol. 24, no. 1, pp. 87-103, 2016.",
        "[7] C. Raleigh et al., 'Introducing ACLED: An armed conflict location and event dataset,' Journal of Peace Research, vol. 47, no. 5, pp. 651-660, 2010.",
        "[8] K. Leetaru and P. A. Schrodt, 'GDELT: Global data on events, location, and tone, 1979-2012,' ISA Annual Convention, 2013.",
        "[9] E. Boschee et al., 'ICEWS Coded Event Data,' Harvard Dataverse, DOI: 10.7910/DVN/28075, 2015.",
        "[10] R. Sundberg and E. Melander, 'Introducing the UCDP georeferenced event dataset,' Journal of Peace Research, vol. 50, no. 4, pp. 523-532, 2013.",
        "[11] N. P. Gleditsch et al., 'Armed conflict 1946-2001: A new dataset,' Journal of Peace Research, vol. 39, no. 5, pp. 615-637, 2002.",
        "[12] S. Chojnacki et al., 'Event data on armed conflict and security,' International Interactions, vol. 38, no. 4, pp. 382-401, 2012.",
        "[13] E. Rossi et al., 'Temporal graph networks for deep learning on dynamic graphs,' arXiv preprint arXiv:2006.10637, 2020.",
        "[14] A. Pareja et al., 'EvolveGCN: Evolving graph convolutional networks for dynamic graphs,' AAAI, vol. 34, no. 04, pp. 5363-5370, 2020.",
        "[15] R. Trivedi et al., 'DyRep: Learning representations over dynamic graphs,' ICML, pp. 6309-6317, 2019.",
        "[16] R. Trivedi et al., 'Know-evolve: Deep temporal reasoning for dynamic knowledge graphs,' ICML, pp. 3462-3471, 2017.",
        "[17] Y. Ma et al., 'Event forecasting with graph neural networks: A survey and benchmark,' ACM Computing Surveys, vol. 55, no. 13, 2023.",
        "[18] G. M. Campedelli et al., 'Learning future terrorist targets through temporal meta-graphs,' AI and Law, vol. 29, no. 4, pp. 461-489, 2021.",
        "[19] T. Hossain et al., 'Identifying precursors to geopolitical events using attention networks,' AAAI, vol. 37, pp. 14234-14242, 2023.",
        "[20] T. N. Kipf and M. Welling, 'Semi-supervised classification with graph convolutional networks,' ICLR, 2017.",
        "[21] P. Veličković et al., 'Graph Attention Networks,' ICLR, 2018.",
        "[22] D. Xu et al., 'Inductive representation learning on temporal graphs,' ICLR, 2020.",
        "[23] J. Devlin et al., 'BERT: Pre-training of deep bidirectional transformers for language understanding,' NAACL-HLT, pp. 4171-4186, 2019.",
        "[24] Y. Liu et al., 'RoBERTa: A robustly optimized BERT pretraining approach,' arXiv preprint arXiv:1907.11692, 2019.",
        "[25] V. Sanh et al., 'DistilBERT, a distilled version of BERT: smaller, faster, cheaper and lighter,' NeurIPS Workshop, 2019.",
        "[26] C. Banea et al., 'Multilingual sentiment analysis for news streams,' ACL, pp. 512-522, 2014.",
        "[27] C. Hutto and E. Gilbert, 'VADER: A parsimonious rule-based model for sentiment analysis,' ICWSM, vol. 8, no. 1, pp. 216-225, 2014.",
        "[28] A. Vaswani et al., 'Attention is all you need,' NeurIPS, vol. 30, pp. 5998-6008, 2017.",
        "[29] A. Radford et al., 'Language models are unsupervised multitask learners,' OpenAI Tech Report, 2019.",
        "[30] N. Reimers and I. Gurevych, 'Sentence-BERT: Sentence embeddings using Siamese BERT-networks,' EMNLP, pp. 3982-3992, 2019.",
        "[31] B. Lim et al., 'Temporal Fusion Transformers for interpretable multi-horizon time series forecasting,' Int. J. Forecast., vol. 37, no. 4, pp. 1748-1764, 2021.",
        "[32] D. Salinas et al., 'DeepAR: Probabilistic forecasting with autoregressive recurrent networks,' Int. J. Forecast., vol. 36, no. 3, pp. 1181-1191, 2020.",
        "[33] G. Zerveas et al., 'A transformer-based framework for multivariate time series representation learning,' KDD, pp. 2114-2124, 2021.",
        "[34] F. T. Liu, K. M. Ting, and Z.-H. Zhou, 'Isolation forest,' IEEE ICDM, pp. 413-422, 2008.",
        "[35] K. J. Mach et al., 'Climate as a risk factor for armed conflict,' Nature, vol. 571, no. 7764, pp. 193-197, 2019.",
        "[36] S. M. Hsiang, M. Burke, and E. Miguel, 'Quantifying the influence of climate on human conflict,' Science, vol. 341, p. 1235367, 2013.",
        "[37] M. Burke, S. M. Hsiang, and E. Miguel, 'Global non-linear effect of temperature on economic production,' Nature, vol. 527, pp. 235-239, 2015.",
        "[38] E. Miguel, S. Satyanath, and E. Sergenti, 'Economic shocks and civil conflict: An instrumental variables approach,' J. Polit. Econ., vol. 112, no. 4, pp. 725-753, 2004.",
        "[39] P. Collier and A. Hoeffler, 'Greed and grievance in civil war,' Oxford Economic Papers, vol. 56, no. 4, pp. 563-595, 2004.",
        "[40] J. D. Fearon and D. D. Laitin, 'Ethnicity, insurgency, and civil war,' American Political Science Review, vol. 97, no. 1, pp. 75-90, 2003.",
        "[41] B. Schölkopf et al., 'Toward causal representation learning,' Proceedings of the IEEE, vol. 109, no. 5, pp. 612-634, 2021.",
        "[42] S. Athey and G. W. Imbens, 'Machine learning methods that economists should know for estimating heterogeneous causal effects,' J. Econ. Perspect., vol. 36, no. 3, pp. 31-54, 2022."
    ]

    for ref in refs:
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.25)
        p.paragraph_format.space_after = Pt(2.5)
        r = p.add_run(ref)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(8.5)

    out_path = os.path.join(os.path.dirname(__file__), "ARES_preprint.docx")
    doc.save(out_path)
    print(f"Preprint manuscript successfully generated at: {out_path}")

if __name__ == "__main__":
    create_preprint_docx()
