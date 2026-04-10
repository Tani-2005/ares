"""
Generates realistic synthetic static datasets representing the actual data sources.
Used when real static files are not present, or to supplement them.
This simulates the kinds of records that ACLED, SIPRI, World Bank, etc. would produce.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

ZONE_A_COUNTRIES = [
    "India", "Pakistan", "China", "Bangladesh", "Sri Lanka", "Nepal",
    "Myanmar", "Thailand", "Vietnam", "Philippines", "Indonesia",
    "Malaysia", "Taiwan", "South Korea", "Japan"
]

ZONE_B_COUNTRIES = [
    "United States", "Russia", "Germany", "France", "United Kingdom", "Canada"
]

ALL_COUNTRIES = ZONE_A_COUNTRIES + ZONE_B_COUNTRIES

ACLED_EVENT_TYPES = [
    "Battles", "Explosions/Remote violence", "Violence against civilians",
    "Riots", "Protests", "Strategic developments"
]

ICEWS_EVENT_TYPES = [
    "Make statement", "Appeal", "Express intent to cooperate",
    "Consult", "Engage in diplomatic cooperation", "Threaten",
    "Demonstrate or rally", "Make empathetic comment",
    "Reduce relations", "Provide aid", "Impose sanctions"
]

SIPRI_CATEGORIES = [
    "Fighter aircraft", "Armoured vehicles", "Naval vessels",
    "Missiles", "Artillery", "Radar systems", "Helicopters"
]

np.random.seed(42)
random.seed(42)


def _date_range(start_year=2018, end_year=2024):
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)
    delta = end - start
    return [start + timedelta(days=random.randint(0, delta.days)) for _ in range(delta.days)]


def generate_acled_data(n=3000) -> pd.DataFrame:
    dates = [datetime(2018, 1, 1) + timedelta(days=i) for i in range(2555)]
    records = []
    for _ in range(n):
        country = random.choice(ZONE_A_COUNTRIES)
        event_date = random.choice(dates)
        event_type = random.choice(ACLED_EVENT_TYPES)
        severity_map = {
            "Battles": np.random.randint(1, 50),
            "Explosions/Remote violence": np.random.randint(0, 20),
            "Violence against civilians": np.random.randint(0, 30),
            "Riots": np.random.randint(0, 15),
            "Protests": np.random.randint(0, 5),
            "Strategic developments": 0
        }
        records.append({
            "event_id_cnty": f"ACLED_{random.randint(100000, 999999)}",
            "event_date": event_date.strftime("%Y-%m-%d"),
            "year": event_date.year,
            "event_type": event_type,
            "sub_event_type": f"{event_type} - variant {random.randint(1,3)}",
            "actor1": f"Military Forces of {country}",
            "actor2": f"Armed Group {random.randint(1,5)}",
            "country": country,
            "location": f"Region {random.randint(1,10)}, {country}",
            "latitude": round(np.random.uniform(-10, 50), 4),
            "longitude": round(np.random.uniform(60, 145), 4),
            "fatalities": severity_map[event_type],
            "source": "ACLED",
            "notes": f"Conflict event in {country}: {event_type}"
        })
    df = pd.DataFrame(records)
    df["event_date"] = pd.to_datetime(df["event_date"])
    return df.sort_values("event_date").reset_index(drop=True)


def generate_icews_data(n=4000) -> pd.DataFrame:
    dates = [datetime(2015, 1, 1) + timedelta(days=i) for i in range(3650)]
    records = []
    goldstein_map = {
        "Make statement": 0.0,
        "Appeal": 1.9,
        "Express intent to cooperate": 3.4,
        "Consult": 5.0,
        "Engage in diplomatic cooperation": 7.4,
        "Threaten": -5.0,
        "Demonstrate or rally": -2.0,
        "Make empathetic comment": 2.5,
        "Reduce relations": -4.4,
        "Provide aid": 6.0,
        "Impose sanctions": -6.0
    }
    for _ in range(n):
        source_country = random.choice(ALL_COUNTRIES)
        target_country = random.choice(ALL_COUNTRIES)
        while target_country == source_country:
            target_country = random.choice(ALL_COUNTRIES)
        event_type = random.choice(ICEWS_EVENT_TYPES)
        event_date = random.choice(dates)
        goldstein = goldstein_map[event_type] + np.random.normal(0, 0.5)
        records.append({
            "event_date": event_date.strftime("%Y-%m-%d"),
            "source_country": source_country,
            "target_country": target_country,
            "event_type": event_type,
            "goldstein_scale": round(goldstein, 2),
            "avg_tone": round(goldstein * 8 + np.random.normal(0, 2), 2),
            "source": "ICEWS"
        })
    df = pd.DataFrame(records)
    df["event_date"] = pd.to_datetime(df["event_date"])
    return df.sort_values("event_date").reset_index(drop=True)


def generate_sipri_data() -> pd.DataFrame:
    records = []
    for year in range(2010, 2025):
        for supplier in ["United States", "Russia", "Germany", "France", "United Kingdom", "China"]:
            recipients = random.sample(ZONE_A_COUNTRIES, random.randint(2, 5))
            for recipient in recipients:
                for category in random.sample(SIPRI_CATEGORIES, random.randint(1, 3)):
                    records.append({
                        "year": year,
                        "supplier": supplier,
                        "recipient": recipient,
                        "category": category,
                        "tiv_millions": round(np.random.exponential(150), 2),
                        "units": random.randint(1, 50),
                        "source": "SIPRI"
                    })
    return pd.DataFrame(records)


def generate_world_bank_gdp() -> pd.DataFrame:
    records = []
    base_gdp = {
        "India": 2.8, "China": 6.0, "Pakistan": 3.5, "Bangladesh": 6.5,
        "United States": 2.3, "Germany": 1.5, "Japan": 0.8, "South Korea": 2.9,
        "Indonesia": 5.0, "Vietnam": 6.5, "Philippines": 5.8, "Malaysia": 4.5,
        "Thailand": 3.5, "Sri Lanka": 3.0, "Myanmar": 5.5, "Taiwan": 3.0,
        "Russia": 1.5, "France": 1.3, "United Kingdom": 1.8, "Canada": 2.0,
        "Nepal": 4.5, "Singapore": 3.5
    }
    for country, base in base_gdp.items():
        for year in range(2010, 2025):
            shock = 0
            if year == 2020:
                shock = -6 + np.random.normal(0, 1)
            elif year == 2021:
                shock = 4 + np.random.normal(0, 1)
            value = base + shock + np.random.normal(0, 0.8)
            records.append({
                "country": country,
                "indicator": "GDP Growth (%)",
                "year": year,
                "value": round(value, 2),
                "source": "World Bank"
            })
    return pd.DataFrame(records)


def generate_world_bank_inflation() -> pd.DataFrame:
    records = []
    base_inflation = {
        "India": 5.5, "China": 2.5, "Pakistan": 9.0, "Bangladesh": 5.8,
        "United States": 2.5, "Germany": 2.0, "Japan": 0.5, "South Korea": 2.5,
        "Indonesia": 4.0, "Vietnam": 3.5, "Philippines": 3.8, "Malaysia": 2.5,
        "Thailand": 2.0, "Sri Lanka": 6.0, "Myanmar": 7.0, "Taiwan": 1.5,
        "Russia": 5.5, "France": 1.5, "United Kingdom": 2.5, "Canada": 2.0,
        "Nepal": 5.0, "Singapore": 1.5
    }
    for country, base in base_inflation.items():
        for year in range(2010, 2025):
            shock = 0
            if year >= 2022:
                shock = 5 + np.random.normal(0, 1.5)
            elif year == 2020:
                shock = -1 + np.random.normal(0, 0.5)
            value = base + shock + np.random.normal(0, 0.7)
            records.append({
                "country": country,
                "indicator": "Inflation CPI (%)",
                "year": year,
                "value": round(max(value, -1), 2),
                "source": "World Bank"
            })
    return pd.DataFrame(records)


def generate_un_sanctions() -> pd.DataFrame:
    records = []
    sanction_targets = ["Iran", "North Korea", "Myanmar", "Russia", "Syria",
                        "Libya", "Sudan", "Yemen", "South Sudan", "Mali"]
    sanction_types = [
        "Arms embargo", "Travel ban", "Asset freeze",
        "Trade restriction", "Financial sanctions", "Oil embargo"
    ]
    for _ in range(500):
        year = random.randint(2000, 2024)
        month = random.randint(1, 12)
        records.append({
            "date": f"{year}-{month:02d}-01",
            "target_country": random.choice(sanction_targets),
            "sanction_type": random.choice(sanction_types),
            "imposing_body": "UN Security Council",
            "resolution": f"UNSC Res {random.randint(1500, 2750)}",
            "source": "UN Sanctions"
        })
    df = pd.DataFrame(records)
    df["date"] = pd.to_datetime(df["date"])
    return df.sort_values("date").reset_index(drop=True)


def generate_un_voting() -> pd.DataFrame:
    records = []
    resolutions = [
        "Palestine State", "Climate Action", "Myanmar sanctions",
        "North Korea disarmament", "Russia Ukraine", "Iran nuclear",
        "South China Sea", "India Pakistan", "ASEAN human rights"
    ]
    for _ in range(300):
        year = random.randint(2000, 2024)
        month = random.randint(1, 12)
        country = random.choice(ALL_COUNTRIES)
        vote = random.choice(["Yes", "No", "Abstain"])
        records.append({
            "date": f"{year}-{month:02d}-01",
            "resolution": random.choice(resolutions),
            "country": country,
            "vote": vote,
            "session": f"UNGA {year - 1945}",
            "source": "UN Voting"
        })
    df = pd.DataFrame(records)
    df["date"] = pd.to_datetime(df["date"])
    return df.sort_values("date").reset_index(drop=True)


def generate_gsdb_data() -> pd.DataFrame:
    records = []
    sender_countries = ["United States", "European Union", "United Kingdom",
                        "Russia", "China", "United Nations"]
    for _ in range(400):
        year = random.randint(1990, 2024)
        month = random.randint(1, 12)
        target = random.choice(ALL_COUNTRIES + ["Iran", "North Korea", "Syria", "Libya"])
        records.append({
            "date": f"{year}-{month:02d}-01",
            "sender": random.choice(sender_countries),
            "target": target,
            "sanction_type": random.choice(["Trade", "Financial", "Arms", "Travel", "Diplomatic"]),
            "active": random.choice([True, True, False]),
            "source": "GSDB"
        })
    df = pd.DataFrame(records)
    df["date"] = pd.to_datetime(df["date"])
    return df.sort_values("date").reset_index(drop=True)


def generate_exchange_rate_data() -> pd.DataFrame:
    records = []
    currencies = {
        "India": ("INR", 65.0),
        "Pakistan": ("PKR", 130.0),
        "China": ("CNY", 6.8),
        "Bangladesh": ("BDT", 85.0),
        "Sri Lanka": ("LKR", 180.0),
        "Vietnam": ("VND", 22000.0),
        "Indonesia": ("IDR", 14000.0),
        "Philippines": ("PHP", 50.0),
        "Malaysia": ("MYR", 4.1),
        "Thailand": ("THB", 33.0),
        "South Korea": ("KRW", 1150.0),
        "Japan": ("JPY", 110.0),
        "Russia": ("RUB", 65.0),
    }
    for country, (currency, base_rate) in currencies.items():
        for year in range(2015, 2025):
            for quarter in range(1, 5):
                drift = (year - 2015) * 0.03 * base_rate
                shock = 0
                if year == 2020 and quarter in [2, 3]:
                    shock = base_rate * 0.08
                rate = base_rate + drift + shock + np.random.normal(0, base_rate * 0.02)
                records.append({
                    "country": country,
                    "currency": currency,
                    "year": year,
                    "quarter": quarter,
                    "usd_rate": round(rate, 4),
                    "source": "Exchange Rate"
                })
    return pd.DataFrame(records)


def generate_weo_data() -> pd.DataFrame:
    records = []
    indicators = [
        ("Current Account Balance (% GDP)", -3.0, 3.0),
        ("Government Debt (% GDP)", 40.0, 120.0),
        ("Fiscal Balance (% GDP)", -5.0, 2.0),
    ]
    for country in ALL_COUNTRIES:
        for indicator, low, high in indicators:
            for year in range(2010, 2025):
                value = np.random.uniform(low, high)
                records.append({
                    "country": country,
                    "indicator": indicator,
                    "year": year,
                    "value": round(value, 2),
                    "source": "IMF WEO"
                })
    return pd.DataFrame(records)


def load_all_static_datasets() -> dict:
    return {
        "acled": generate_acled_data(),
        "icews": generate_icews_data(),
        "sipri": generate_sipri_data(),
        "world_bank_gdp": generate_world_bank_gdp(),
        "world_bank_inflation": generate_world_bank_inflation(),
        "un_sanctions": generate_un_sanctions(),
        "un_voting": generate_un_voting(),
        "gsdb": generate_gsdb_data(),
        "exchange_rate": generate_exchange_rate_data(),
        "weo": generate_weo_data()
    }
