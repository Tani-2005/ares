# Workspace

## Overview

pnpm workspace monorepo using TypeScript. Each package manages its own dependencies.
Also contains an ARES (Advanced Reconnaissance & Escalation System) Python/Streamlit dashboard.

## Stack

- **Monorepo tool**: pnpm workspaces
- **Node.js version**: 24
- **Package manager**: pnpm
- **TypeScript version**: 5.9
- **API framework**: Express 5
- **Database**: PostgreSQL + Drizzle ORM
- **Validation**: Zod (`zod/v4`), `drizzle-zod`
- **API codegen**: Orval (from OpenAPI spec)
- **Build**: esbuild (CJS bundle)

## Key Commands

- `pnpm run typecheck` — full typecheck across all packages
- `pnpm run build` — typecheck + build all packages
- `pnpm --filter @workspace/api-spec run codegen` — regenerate API hooks and Zod schemas from OpenAPI spec
- `pnpm --filter @workspace/db run push` — push DB schema changes (dev only)
- `pnpm --filter @workspace/api-server run dev` — run API server locally

See the `pnpm-workspace` skill for workspace structure, TypeScript setup, and package details.

---

## ARES Dashboard

**Location**: `artifacts/ares-dashboard/`

**Description**: AI-powered Regional Escalation Sentinel for the Indo-Pacific region.
Demonstrates data collection, preprocessing, and feature engineering pipeline.

### Tech Stack (Python)
- **Runtime**: Python 3.11
- **Frontend**: Streamlit 1.56 on port 8000
- **Data Processing**: Pandas, NumPy
- **ML**: Scikit-Learn (IsolationForest, feature importance)
- **Visualization**: Plotly Express, Plotly Graph Objects
- **Database**: SQLite (`data/master_data.db`)
- **Live Data**: GDELT API (news events)
- **Config**: `config.yaml`

### Workflow
- **Workflow name**: ARES Dashboard
- **Command**: `cd artifacts/ares-dashboard && streamlit run app.py --server.port 8000 ...`
- **Port**: 8000

### Data Sources Integrated
| Source | Type | Records |
|--------|------|---------|
| ACLED | Conflict Events | ~3,000 |
| ICEWS (Harvard) | Diplomatic Events | ~4,000 |
| GDELT (Live) | News Events | ~50–250 |
| SIPRI | Arms Transfers | ~639 |
| World Bank GDP | Economic | ~330 |
| World Bank Inflation | Economic | ~330 |
| IMF WEO | Economic | ~945 |
| Exchange Rates | Economic | ~520 |
| UN Sanctions | Diplomatic | ~500 |
| UN Voting | Diplomatic | ~300 |
| GSDB | Sanctions | ~400 |

### Dashboard Pages
1. **Overview** — Mission status metrics, risk distribution, pipeline stage results
2. **Data Sources** — Source cards, ingestion log, record charts
3. **Preprocessing** — Data quality, missing values, processing log
4. **Feature Engineering** — Feature matrix, importance, rolling window comparison
5. **Country Analysis** — Per-country deep-dive with 90-day trend charts

### Architecture (`artifacts/ares-dashboard/src/`)
- `database.py` — SQLite schema, CRUD helpers
- `static_data_generator.py` — Synthetic static dataset generation
- `ingestion.py` — Live GDELT + static data ingestion
- `preprocessing.py` — Date normalization, deduplication, outlier clipping
- `feature_engineering.py` — Rolling features, risk scoring, anomaly detection
- `pipeline.py` — End-to-end orchestrator
