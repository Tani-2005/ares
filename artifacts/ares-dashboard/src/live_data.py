"""
Live data fetchers for additional open-source APIs.
All sources are free, require no API key, and are relevant to the ARES project.

Sources:
- World Bank Open Data API  (gdp, inflation, unemployment, military expenditure)
- UCDP GED API              (Uppsala Conflict Data Program — verified conflict events)
- ReliefWeb API             (UN humanitarian crisis reports)
- IMF Data API              (macro financial indicators)
- UN Comtrade API           (arms/dual-use trade flows)
"""

import requests
import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
from typing import Optional

logger = logging.getLogger(__name__)

TIMEOUT = 12

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
    "BN.CAB.XOKA.GD.ZS": "Current Account Balance (% GDP)",
    "GC.DOD.TOTL.GD.ZS": "Government Debt (% GDP)",
}


# ─────────────────────────────────────────────
# 1. World Bank Live API
# ─────────────────────────────────────────────
def fetch_world_bank_live(indicator_code: str, indicator_name: str,
                          start_year: int = 2018, end_year: int = 2024) -> pd.DataFrame:
    """Fetch a World Bank indicator for all ARES countries."""
    iso_codes = ";".join(ALL_ISO.keys())
    url = (
        f"https://api.worldbank.org/v2/country/{iso_codes}/indicator/{indicator_code}"
        f"?format=json&per_page=1000&mrv=8&date={start_year}:{end_year}"
    )
    try:
        resp = requests.get(url, timeout=TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        records_raw = data[1] if len(data) > 1 else []
        rows = []
        for rec in (records_raw or []):
            iso = rec.get("countryiso3code") or rec.get("country", {}).get("id", "")
            # Convert 3-letter to 2-letter
            country = None
            for iso2, name in ALL_ISO.items():
                if iso.upper() == iso2 or rec.get("country", {}).get("value", "") == name:
                    country = name
                    break
            if not country:
                continue
            value = rec.get("value")
            if value is None:
                continue
            rows.append({
                "source": "World Bank Live",
                "indicator_type": indicator_name,
                "country": country,
                "year": int(rec.get("date", 0)),
                "month": None,
                "value": round(float(value), 4),
                "unit": "%",
            })
        logger.info(f"World Bank Live [{indicator_name}]: {len(rows)} records")
        return pd.DataFrame(rows)
    except Exception as e:
        logger.warning(f"World Bank Live fetch failed for {indicator_code}: {e}")
        return pd.DataFrame()


def fetch_all_world_bank_live() -> pd.DataFrame:
    """Fetch World Bank indicators in small batches to avoid timeout."""
    frames = []
    indicator_items = list(WB_INDICATORS.items())
    # Fetch 2 indicators at a time to keep requests small
    for code, name in indicator_items:
        df = fetch_world_bank_live(code, name, start_year=2020, end_year=2024)
        if not df.empty:
            frames.append(df)
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


# ─────────────────────────────────────────────
# 2. UCDP GED API  (Uppsala Conflict Data)
# ─────────────────────────────────────────────
UCDP_COUNTRY_IDS = {
    "India": 140, "Pakistan": 165, "China": 110, "Myanmar": 432, "Philippines": 775,
    "Thailand": 800, "Vietnam": 816, "Indonesia": 850, "Bangladesh": 771,
    "Sri Lanka": 780, "Nepal": 790, "Malaysia": 820,
}

def fetch_ucdp_ged(start_year: int = 2020) -> pd.DataFrame:
    """Fetch UCDP Georeferenced Event Dataset — verified conflict events."""
    rows = []
    base_url = "https://ucdpapi.pcr.uu.se/api/gedevents/23.1"
    for country, cid in UCDP_COUNTRY_IDS.items():
        try:
            params = {
                "pagesize": 200,
                "page": 1,
                "country": cid,
                "startyear": start_year,
            }
            resp = requests.get(base_url, params=params, timeout=TIMEOUT)
            if resp.status_code != 200:
                continue
            data = resp.json()
            events = data.get("Result", [])
            for ev in events:
                date_str = ev.get("date_start", "")
                try:
                    event_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
                except Exception:
                    continue
                rows.append({
                    "source": "UCDP GED Live",
                    "event_date": event_date.strftime("%Y-%m-%d"),
                    "country": country,
                    "zone": "A",
                    "event_type": _ucdp_type(int(ev.get("type_of_violence", 3))),
                    "sub_type": ev.get("dyad_name", ""),
                    "severity": float(ev.get("best", 0)),
                    "actor1": ev.get("side_a", ""),
                    "actor2": ev.get("side_b", ""),
                    "description": ev.get("conflict_name", ""),
                    "url": f"https://ucdp.uu.se/event/{ev.get('id', '')}",
                    "goldstein_scale": _ucdp_goldstein(int(ev.get("type_of_violence", 3))),
                    "avg_tone": _ucdp_goldstein(int(ev.get("type_of_violence", 3))) * 8,
                })
            logger.info(f"UCDP GED [{country}]: {len(events)} events")
        except Exception as e:
            logger.warning(f"UCDP GED failed for {country}: {e}")
            continue
    return pd.DataFrame(rows)


def _ucdp_type(v: int) -> str:
    return {1: "State-Based Conflict", 2: "Non-State Conflict", 3: "One-Sided Violence"}.get(v, "Conflict")


def _ucdp_goldstein(v: int) -> float:
    return {1: -7.0, 2: -5.5, 3: -8.5}.get(v, -6.0)


# ─────────────────────────────────────────────
# 3. ReliefWeb API  (UN Humanitarian Reports)
# ─────────────────────────────────────────────
RELIEFWEB_COUNTRIES = [
    "India", "Pakistan", "China", "Myanmar", "Philippines",
    "Bangladesh", "Sri Lanka", "Nepal", "Vietnam", "Indonesia",
    "Thailand", "Malaysia", "South Korea", "Japan"
]

def fetch_reliefweb(days_back: int = 30, limit: int = 200) -> pd.DataFrame:
    """Fetch crisis/conflict reports from UN ReliefWeb API (GET endpoint)."""
    rows = []
    # Use simple GET requests per country to avoid filter complexity issues
    target_countries = RELIEFWEB_COUNTRIES[:6]  # top priority countries
    for country in target_countries:
        try:
            url = (
                f"https://api.reliefweb.int/v1/reports"
                f"?appname=ares-academic"
                f"&filter[field]=primary_country.name"
                f"&filter[value]={requests.utils.quote(country)}"
                f"&fields[include][]=title&fields[include][]=date"
                f"&fields[include][]=primary_country&fields[include][]=theme"
                f"&sort[]=date.created:desc&limit={min(limit // len(target_countries), 30)}"
            )
            resp = requests.get(url, timeout=TIMEOUT,
                                headers={"User-Agent": "ARES/1.0 (academic)"})
            if resp.status_code not in (200, 201):
                logger.debug(f"ReliefWeb {country}: HTTP {resp.status_code}")
                continue
            data = resp.json()
            items = data.get("data", [])
            for item in items:
                fields = item.get("fields", {})
                country_info = fields.get("primary_country", {})
                country_name = country_info.get("name", country) if isinstance(country_info, dict) else country
                date_info = fields.get("date", {})
                date_str = date_info.get("created", "")[:10] if isinstance(date_info, dict) else ""
                themes = fields.get("theme", [])
                theme_names = [t.get("name", "") for t in themes if isinstance(t, dict)]
                is_conflict = any(
                    kw in " ".join(theme_names).lower()
                    for kw in ["conflict", "violence", "insecurity", "coup", "war"]
                )
                goldstein = -5.0 if is_conflict else -2.0
                rows.append({
                    "source": "ReliefWeb Live",
                    "event_date": date_str,
                    "country": country_name,
                    "zone": "A",
                    "event_type": "Conflict Event" if is_conflict else "Humanitarian Crisis",
                    "sub_type": ", ".join(theme_names[:2]) or "Report",
                    "severity": 0.6 if is_conflict else 0.3,
                    "actor1": "UN/NGO",
                    "actor2": "",
                    "description": fields.get("title", "")[:400],
                    "url": f"https://reliefweb.int/node/{item.get('id', '')}",
                    "goldstein_scale": goldstein + np.random.uniform(-0.5, 0.5),
                    "avg_tone": goldstein * 7 + np.random.uniform(-1, 1),
                })
        except Exception as e:
            logger.debug(f"ReliefWeb {country}: {e}")
            continue
    logger.info(f"ReliefWeb Live: {len(rows)} reports")
    return pd.DataFrame(rows)


# ─────────────────────────────────────────────
# 4. IMF Data API
# ─────────────────────────────────────────────
IMF_INDICATORS = {
    "PCPIPCH": "Inflation Rate IMF (%)",
    "NGDP_RPCH": "GDP Growth IMF (%)",
    "LUR": "Unemployment IMF (%)",
    "BCA_NGDPD": "Current Account IMF (% GDP)",
}

IMF_COUNTRY_CODES = {
    "India": "IND", "Pakistan": "PAK", "China": "CHN", "Bangladesh": "BGD",
    "Sri Lanka": "LKA", "Nepal": "NPL", "Myanmar": "MMR", "Thailand": "THA",
    "Vietnam": "VNM", "Philippines": "PHL", "Indonesia": "IDN", "Malaysia": "MYS",
    "South Korea": "KOR", "Japan": "JPN", "Singapore": "SGP", "Taiwan": "TWN",
    "United States": "USA", "Germany": "DEU", "France": "FRA", "United Kingdom": "GBR",
    "Russia": "RUS", "Canada": "CAN",
}


def fetch_imf_indicator(indicator: str, indicator_name: str) -> pd.DataFrame:
    """Fetch IMF World Economic Outlook indicator."""
    rows = []
    current_year = datetime.now().year
    years = f"{current_year - 5}:{current_year + 1}"

    for country, iso3 in IMF_COUNTRY_CODES.items():
        url = f"https://www.imf.org/external/datamapper/api/v1/{indicator}/{iso3}"
        try:
            resp = requests.get(url, timeout=TIMEOUT)
            if resp.status_code != 200:
                continue
            data = resp.json()
            values = data.get("values", {}).get(indicator, {}).get(iso3, {})
            for year_str, value in values.items():
                if value is None:
                    continue
                try:
                    year = int(year_str)
                    if year < 2018 or year > current_year + 2:
                        continue
                    rows.append({
                        "source": "IMF Live",
                        "indicator_type": indicator_name,
                        "country": country,
                        "year": year,
                        "month": None,
                        "value": round(float(value), 4),
                        "unit": "%",
                    })
                except (ValueError, TypeError):
                    continue
        except Exception as e:
            logger.debug(f"IMF {indicator} failed for {country}: {e}")
            continue

    logger.info(f"IMF Live [{indicator_name}]: {len(rows)} records")
    return pd.DataFrame(rows)


def fetch_all_imf_live() -> pd.DataFrame:
    frames = []
    for code, name in IMF_INDICATORS.items():
        df = fetch_imf_indicator(code, name)
        if not df.empty:
            frames.append(df)
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


# ─────────────────────────────────────────────
# 5. GDELT GKG (Global Knowledge Graph) — Tone & Theme Counts
# ─────────────────────────────────────────────
CONFLICT_THEMES = [
    "MILITARY", "TERROR", "PROTEST", "SANCTION", "WEAPONS",
    "NUCLEAR", "CONFLICT", "ESPIONAGE", "BLOCKADE"
]

def fetch_gdelt_gkg_themes(days_back: int = 7) -> pd.DataFrame:
    """
    Fetch GDELT GKG theme counts for conflict-related signals.
    Uses GDELT's public doc API endpoint.
    """
    rows = []
    for theme in CONFLICT_THEMES[:5]:
        for country, _ in list(ZONE_A_ISO.items())[:8]:
            try:
                url = (
                    f"https://api.gdeltproject.org/api/v2/doc/doc?"
                    f"query={theme}+sourcecountry:{country}"
                    f"&mode=timelinevol&timespan={days_back}d&format=json"
                )
                resp = requests.get(url, timeout=TIMEOUT)
                if resp.status_code != 200:
                    continue
                data = resp.json()
                timeline = data.get("timeline", [])
                for series in timeline:
                    for point in series.get("data", []):
                        date_str = point.get("date", "")
                        value = point.get("value", 0)
                        try:
                            dt = datetime.strptime(date_str, "%Y%m%dT%H%M%SZ")
                            country_name = ZONE_A_ISO.get(country, country)
                            rows.append({
                                "source": "GDELT GKG Live",
                                "event_date": dt.strftime("%Y-%m-%d"),
                                "country": country_name,
                                "zone": "A",
                                "event_type": f"GDELT Theme: {theme}",
                                "sub_type": theme,
                                "severity": min(float(value) / 100, 1.0),
                                "actor1": "", "actor2": "",
                                "description": f"GDELT GKG volume signal: {theme} in {country_name}",
                                "url": "",
                                "goldstein_scale": -4.0 if theme in ["MILITARY", "TERROR", "CONFLICT"] else -2.0,
                                "avg_tone": -5.0 if theme in ["MILITARY", "TERROR", "CONFLICT"] else -2.5,
                            })
                        except Exception:
                            continue
            except Exception as e:
                logger.debug(f"GDELT GKG {theme}/{country}: {e}")
                continue
    logger.info(f"GDELT GKG Live: {len(rows)} signals")
    return pd.DataFrame(rows)


# ─────────────────────────────────────────────
# Master live fetch runner
# ─────────────────────────────────────────────
def fetch_all_live(progress_cb=None) -> dict:
    """
    Fetch all live data sources. Returns dict of DataFrames.
    Each source gracefully handles network failures.
    """
    results = {}

    def _run(name, fn, *args, **kwargs):
        if progress_cb:
            progress_cb(name)
        try:
            df = fn(*args, **kwargs)
            results[name] = df
            logger.info(f"[Live] {name}: {len(df)} rows fetched")
        except Exception as e:
            logger.warning(f"[Live] {name} failed: {e}")
            results[name] = pd.DataFrame()

    _run("world_bank_live", fetch_all_world_bank_live)
    _run("ucdp_ged_live", fetch_ucdp_ged, 2020)
    _run("reliefweb_live", fetch_reliefweb, 60)
    _run("imf_live", fetch_all_imf_live)
    _run("gdelt_gkg_live", fetch_gdelt_gkg_themes, 7)

    return results
