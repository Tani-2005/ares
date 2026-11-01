"""
Optimized live data fetchers for open-source APIs.
Uses ThreadPoolExecutor for fast non-blocking concurrent requests.
Graceful timeouts (3.5s) and DNS pre-checks eliminate the 15-minute pipeline stall.

Sources:
- World Bank Open Data API
- UCDP GED API (with fast-fail DNS check)
- UN ReliefWeb API
- IMF Datamapper API
- GDELT GKG Theme Signals
"""

import requests
import socket
import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)

TIMEOUT = 3.5  # Fast 3.5s timeout prevents hanging

ZONE_A_ISO = {
    "IN": "India", "PK": "Pakistan", "CN": "China", "BD": "Bangladesh",
    "LK": "Sri Lanka", "NP": "Nepal", "MM": "Myanmar", "TH": "Thailand",
    "VN": "Vietnam", "PH": "Philippines", "ID": "Indonesia", "MY": "Malaysia",
    "SG": "Singapore", "KR": "South Korea", "JP": "Japan", "TW": "Taiwan",
}
ZONE_B_ISO = {
    "US": "United States", "CA": "Canada", "DE": "Germany",
    "FR": "France", "GB": "United Kingdom", "RU": "Russia",
}
ALL_ISO = {**ZONE_A_ISO, **ZONE_B_ISO}

WB_INDICATORS = {
    "NY.GDP.MKTP.KD.ZG": "GDP Growth (%)",
    "FP.CPI.TOTL.ZG":    "Inflation CPI (%)",
    "SL.UEM.TOTL.ZS":    "Unemployment Rate (%)",
    "MS.MIL.XPND.GD.ZS": "Military Expenditure (% GDP)",
}


def _is_host_reachable(host: str, port: int = 443, timeout: float = 1.0) -> bool:
    """Quick 1-second socket check to avoid waiting on dead DNS/APIs."""
    try:
        sock = socket.create_connection((host, port), timeout=timeout)
        sock.close()
        return True
    except Exception:
        return False


# ─────────────────────────────────────────────
# 1. World Bank Live API (Concurrent Batching)
# ─────────────────────────────────────────────
def fetch_world_bank_single(code: str, name: str) -> pd.DataFrame:
    iso_codes = ";".join(list(ALL_ISO.keys())[:15])
    url = (
        f"https://api.worldbank.org/v2/country/{iso_codes}/indicator/{code}"
        f"?format=json&per_page=500&mrv=5&date=2020:2024"
    )
    try:
        resp = requests.get(url, timeout=TIMEOUT)
        if resp.status_code != 200:
            return pd.DataFrame()
        data = resp.json()
        records_raw = data[1] if len(data) > 1 else []
        rows = []
        for rec in (records_raw or []):
            iso = rec.get("countryiso3code") or rec.get("country", {}).get("id", "")
            country = None
            for iso2, cname in ALL_ISO.items():
                if iso.upper() == iso2 or rec.get("country", {}).get("value", "") == cname:
                    country = cname
                    break
            if not country or rec.get("value") is None:
                continue
            rows.append({
                "source": "World Bank Live",
                "indicator_type": name,
                "country": country,
                "year": int(rec.get("date", 0)),
                "month": None,
                "value": round(float(rec.get("value", 0)), 4),
                "unit": "%",
            })
        return pd.DataFrame(rows)
    except Exception as e:
        logger.debug(f"World Bank [{name}] skipped: {e}")
        return pd.DataFrame()


def fetch_all_world_bank_live() -> pd.DataFrame:
    """Fetch World Bank indicators concurrently."""
    frames = []
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(fetch_world_bank_single, code, name) for code, name in WB_INDICATORS.items()]
        for f in as_completed(futures):
            df = f.result()
            if not df.empty:
                frames.append(df)
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


# ─────────────────────────────────────────────
# 2. UCDP GED API (With Fast-Fail Host Probe)
# ─────────────────────────────────────────────
UCDP_COUNTRY_IDS = {
    "India": 140, "Pakistan": 165, "China": 110, "Myanmar": 432, "Philippines": 775
}

def fetch_ucdp_ged(start_year: int = 2020) -> pd.DataFrame:
    """Fetch UCDP Georeferenced Event Dataset. Skips in 0.5s if host unreachable."""
    if not _is_host_reachable("ucdpapi.pcr.uu.se", 443, timeout=0.8):
        logger.info("UCDP API host unreachable; fast-skipping UCDP live fetch.")
        return pd.DataFrame()

    rows = []
    base_url = "https://ucdpapi.pcr.uu.se/api/gedevents/23.1"
    for country, cid in UCDP_COUNTRY_IDS.items():
        try:
            resp = requests.get(base_url, params={"pagesize": 100, "page": 1, "country": cid, "startyear": start_year}, timeout=TIMEOUT)
            if resp.status_code != 200:
                continue
            data = resp.json()
            for ev in data.get("Result", []):
                date_str = ev.get("date_start", "")[:10]
                rows.append({
                    "source": "UCDP GED Live",
                    "event_date": date_str,
                    "country": country,
                    "zone": "A",
                    "event_type": "Conflict Incident",
                    "sub_type": ev.get("dyad_name", ""),
                    "severity": float(ev.get("best", 0)),
                    "actor1": ev.get("side_a", ""),
                    "actor2": ev.get("side_b", ""),
                    "description": ev.get("conflict_name", ""),
                    "url": f"https://ucdp.uu.se/event/{ev.get('id', '')}",
                    "goldstein_scale": -6.5,
                    "avg_tone": -8.0,
                })
        except Exception:
            break
    return pd.DataFrame(rows)


# ─────────────────────────────────────────────
# 3. ReliefWeb API
# ─────────────────────────────────────────────
def _fetch_reliefweb_country(country: str) -> List[Dict]:
    rows = []
    try:
        url = (
            f"https://api.reliefweb.int/v1/reports"
            f"?appname=ares-academic&filter[field]=primary_country.name"
            f"&filter[value]={requests.utils.quote(country)}"
            f"&fields[include][]=title&fields[include][]=date&sort[]=date.created:desc&limit=15"
        )
        resp = requests.get(url, timeout=TIMEOUT, headers={"User-Agent": "ARES/1.0 (academic)"})
        if resp.status_code == 200:
            data = resp.json()
            for item in data.get("data", []):
                fields = item.get("fields", {})
                title = fields.get("title", "")
                is_conflict = any(k in title.lower() for k in ["clash", "conflict", "violence", "border", "military", "crisis"])
                rows.append({
                    "source": "ReliefWeb Live",
                    "event_date": str(fields.get("date", {}).get("created", ""))[:10] or datetime.now().strftime("%Y-%m-%d"),
                    "country": country,
                    "zone": "A",
                    "event_type": "Humanitarian & Security Report",
                    "sub_type": "ReliefWeb Alert",
                    "severity": 0.6 if is_conflict else 0.3,
                    "actor1": "UN / INGO",
                    "actor2": "",
                    "description": title[:300],
                    "url": f"https://reliefweb.int/node/{item.get('id', '')}",
                    "goldstein_scale": -4.5 if is_conflict else -1.5,
                    "avg_tone": -6.0 if is_conflict else -2.0,
                })
    except Exception:
        pass
    return rows


def fetch_reliefweb(days_back: int = 30, limit: int = 60) -> pd.DataFrame:
    countries = ["India", "Pakistan", "China", "Myanmar", "Philippines"]
    all_rows = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(_fetch_reliefweb_country, c) for c in countries]
        for f in as_completed(futures):
            all_rows.extend(f.result())
    return pd.DataFrame(all_rows)


# ─────────────────────────────────────────────
# 4. IMF Data API (Concurrent Strategic Set)
# ─────────────────────────────────────────────
IMF_PRIORITY_COUNTRIES = {
    "India": "IND", "Pakistan": "PAK", "China": "CHN",
    "United States": "USA", "Russia": "RUS"
}
IMF_INDICATORS = {
    "PCPIPCH": "Inflation Rate IMF (%)",
    "NGDP_RPCH": "GDP Growth IMF (%)",
}

def _fetch_imf_single(ind: str, ind_name: str, country: str, iso3: str) -> List[Dict]:
    rows = []
    url = f"https://www.imf.org/external/datamapper/api/v1/{ind}/{iso3}"
    try:
        resp = requests.get(url, timeout=TIMEOUT)
        if resp.status_code == 200:
            data = resp.json()
            values = data.get("values", {}).get(ind, {}).get(iso3, {})
            current_year = datetime.now().year
            for year_str, value in list(values.items())[-3:]:
                rows.append({
                    "source": "IMF Live",
                    "indicator_type": ind_name,
                    "country": country,
                    "year": int(year_str),
                    "month": None,
                    "value": round(float(value), 4),
                    "unit": "%",
                })
    except Exception:
        pass
    return rows


def fetch_all_imf_live() -> pd.DataFrame:
    all_rows = []
    tasks = []
    with ThreadPoolExecutor(max_workers=6) as executor:
        for ind, ind_name in IMF_INDICATORS.items():
            for c, iso in IMF_PRIORITY_COUNTRIES.items():
                tasks.append(executor.submit(_fetch_imf_single, ind, ind_name, c, iso))
        for t in as_completed(tasks):
            all_rows.extend(t.result())
    return pd.DataFrame(all_rows)


# ─────────────────────────────────────────────
# 5. GDELT GKG Themes
# ─────────────────────────────────────────────
def fetch_gdelt_gkg_themes(days_back: int = 7) -> pd.DataFrame:
    """Fetch high-priority theme signals with fast rate-limit protection."""
    rows = []
    themes = ["MILITARY", "PROTEST", "CONFLICT"]
    countries = ["IN", "PK", "CN"]

    for theme in themes:
        for c in countries:
            try:
                url = (
                    f"https://api.gdeltproject.org/api/v2/doc/doc?"
                    f"query={theme}+sourcecountry:{c}&mode=timelinevol&timespan={days_back}d&format=json"
                )
                resp = requests.get(url, timeout=TIMEOUT)
                if resp.status_code == 429:
                    logger.info("GDELT rate limit encountered; stopping GKG query safely.")
                    return pd.DataFrame(rows)
                if resp.status_code != 200:
                    continue
                data = resp.json()
                cname = ZONE_A_ISO.get(c, c)
                rows.append({
                    "source": "GDELT GKG Live",
                    "event_date": datetime.now().strftime("%Y-%m-%d"),
                    "country": cname,
                    "zone": "A",
                    "event_type": f"GDELT Theme: {theme}",
                    "sub_type": theme,
                    "severity": 0.5,
                    "actor1": "", "actor2": "",
                    "description": f"GDELT Theme Signal: {theme} activity in {cname}",
                    "url": "",
                    "goldstein_scale": -4.0,
                    "avg_tone": -5.5,
                })
            except Exception:
                continue
    return pd.DataFrame(rows)
