# app.py
from fastapi import FastAPI
import requests
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()  # loads .env if present

app = FastAPI(title="Jeju (World Bank) → Gemini API")

# CONFIG
COUNTRY_CODE = "KOR"   # South Korea (World Bank country code)
JEJU_LABEL = "Jeju-si"
WORLD_BANK_BASE = "https://api.worldbank.org/v2"
# If you later have a Gemini key, put it in .env as GEMINI_API_KEY
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", None)


# ---------- Helper: fetch indicator from World Bank ----------
def fetch_indicator(country_code: str, indicator_code: str, per_page: int = 100):
    """
    Fetches the indicator series for a country from the World Bank.
    Returns the most recent non-null value as {value, date} or None if not found.
    """
    url = f"{WORLD_BANK_BASE}/country/{country_code}/indicator/{indicator_code}"
    params = {"format": "json", "per_page": per_page}
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    # World Bank returns [metadata, data_list]
    if not data or len(data) < 2:
        return None

    series = data[1]  # list of yearly entries, newest first usually
    for entry in series:
        if entry.get("value") is not None:
            return {"value": entry["value"], "date": entry["date"]}
    return None


# ---------- Normalizer: gather the indicators we want ----------
DEFAULT_INDICATORS = {
    "population": "SP.POP.TOTL",
    "gdp_per_capita_usd": "NY.GDP.PCAP.CD",
    "unemployment_percent": "SL.UEM.TOTL.ZS",
    # add other codes you find on World Bank site for health, electricity, housing proxies
    # "physicians_per_1000": "SH.MED.PHYS.ZS"  # example — verify exact code on WB site
}

def gather_country_indicators(country_code: str, indicators: dict = DEFAULT_INDICATORS):
    out = {}
    for key, code in indicators.items():
        try:
            item = fetch_indicator(country_code, code)
            out[key] = item  # can be None if not found
        except Exception as e:
            out[key] = {"error": str(e)}
    return out


# ---------- Gemini wrapper (placeholder) ----------
def gemini_insight_generate(normalized_payload: dict) -> dict:
    """
    Placeholder for calling Gemini. If GEMINI_API_KEY is set and you have
    the client library, you can call the model here.

    For now this returns a simple template summary.
    Replace the body with actual Gemini SDK calls if you have credentials.
    """
    # BASIC heuristic summary (fallback)
    inds = normalized_payload.get("indicators", {})
    pop = inds.get("population", {}).get("value")
    gdp = inds.get("gdp_per_capita_usd", {}).get("value")
    unemp = inds.get("unemployment_percent", {}).get("value")

    summary = []
    if gdp:
        summary.append(f"South Korea's GDP per capita is about {round(gdp):,} USD (country-level).")
    if unemp is not None:
        summary.append(f"Unemployment is {unemp}% (country-level).")
    if pop:
        summary.append(f"Population (country) is {int(pop):,} people.")

    return {
        "summary": " ".join(summary) or "No summary available.",
        "generated_at": int(datetime.utcnow().timestamp()),
        "notes": "This summary uses World Bank country-level indicators as context for Jeju-si. Replace with real Gemini call if available."
    }

# (If you have google.generativeai, you could implement a real call here:
# import google.generativeai as genai
# genai.configure(api_key=GEMINI_API_KEY)
# ... build prompt and call model ...
# )


# ---------- API endpoints ----------
@app.get("/jeju/opportunity")
def jeju_opportunity():
    """
    Returns country-level indicators from World Bank (used as context for Jeju-si).
    """
    indicators = gather_country_indicators(COUNTRY_CODE)
    response = {
        "location": JEJU_LABEL,
        "country_code": COUNTRY_CODE,
        "indicators": indicators,
        "fetched_at": int(datetime.utcnow().timestamp()),
        "note": "Indicators are country-level (World Bank). For Jeju-specific data, add KOSIS/data.go.kr."
    }
    return response


@app.get("/jeju/profile")
def jeju_profile():
    """
    Combined endpoint: fetch indicators and produce a Gemini-style insight (placeholder).
    """
    indicators = gather_country_indicators(COUNTRY_CODE)
    payload = {
        "location": JEJU_LABEL,
        "country_code": COUNTRY_CODE,
        "indicators": indicators,
        "fetched_at": int(datetime.utcnow().timestamp())
    }
    insight = gemini_insight_generate({"indicators": indicators, "location": JEJU_LABEL})
    payload["insight"] = insight
    return payload
