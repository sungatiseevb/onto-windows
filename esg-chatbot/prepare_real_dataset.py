import re
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
INPUT_XLSX = RAW_DIR / "df_asst_bnk_ecb.xlsx"
OUTPUT_CSV = PROCESSED_DIR / "df_asst_bnk_ecb_clean.csv"


QUAL_MAP = {
    "very good": 4.0,
    "good": 3.0,
    "moderate": 2.0,
    "basic": 1.0,
    "poor": 0.0,
    "qualitative": 2.0,
    "documented": 3.0,
    "esrs-aligned": 3.0,
    "high compliance": 4.0,
}


def parse_number(text: object) -> float | None:
    if pd.isna(text):
        return None
    s = str(text).strip().lower()
    if not s:
        return None

    s = s.replace(",", "")
    # Keep scientific-style contexts simple by taking first numeric mention.
    match = re.search(r"[-+]?\d*\.?\d+", s)
    if not match:
        return None

    val = float(match.group())

    # Scale words often used in this file.
    if "kton" in s:
        val *= 1_000
    elif "million" in s or "m " in s:
        val *= 1_000_000
    elif "bn" in s or "billion" in s:
        val *= 1_000_000_000

    return val


def parse_qualitative(text: object) -> float | None:
    if pd.isna(text):
        return None
    s = str(text).strip().lower()
    if not s:
        return None
    for key, val in QUAL_MAP.items():
        if key in s:
            return val
    return None


def parse_percent_or_number(text: object) -> float | None:
    if pd.isna(text):
        return None
    s = str(text)
    val = parse_number(s)
    if val is None:
        return parse_qualitative(s)
    if "%" in s:
        return val / 100.0
    return val


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    if not INPUT_XLSX.exists():
        raise FileNotFoundError(f"Input file not found: {INPUT_XLSX}")

    raw = pd.read_excel(INPUT_XLSX, sheet_name="Dataset")

    clean = pd.DataFrame()
    clean["bank"] = raw["Banks"].astype(str).str.strip()
    clean["type_code"] = raw["Type"].astype(str).str.strip()
    clean["scope1_emissions"] = raw["Scope 1 GHG emissions"].apply(parse_number)
    clean["scope2_emissions"] = raw["Scope 2 GHG emissions"].apply(parse_number)
    clean["scope3_emissions"] = raw["Scope 3 GHG emissions"].apply(parse_number)
    clean["emission_reduction_score"] = raw["Emission reduction policy"].apply(parse_qualitative)
    clean["renewable_energy_share"] = raw["Renewable energy share"].apply(parse_percent_or_number)
    clean["community_investment"] = raw["Community investment"].apply(parse_number)
    clean["diversity_women_ratio"] = raw["Diversity / Women representation"].apply(parse_percent_or_number)
    clean["health_safety_score"] = raw["Health & Safety"].apply(parse_qualitative)
    clean["board_esg_oversight_score"] = raw["Board strategy / ESG oversight"].apply(parse_qualitative)
    clean["sustainable_finance"] = raw["Sustainable finance / Green financing"].apply(parse_number)
    clean["total_revenue"] = raw["Total revenue"].apply(parse_number)
    clean["reporting_quality_score"] = raw["Reporting quality"].apply(parse_qualitative)

    # Numeric-only frame for causal methods.
    numeric_cols = [
        "scope1_emissions",
        "scope2_emissions",
        "scope3_emissions",
        "emission_reduction_score",
        "renewable_energy_share",
        "community_investment",
        "diversity_women_ratio",
        "health_safety_score",
        "board_esg_oversight_score",
        "sustainable_finance",
        "total_revenue",
        "reporting_quality_score",
    ]
    model_df = clean[numeric_cols].copy()
    model_df = model_df.apply(pd.to_numeric, errors="coerce")
    model_df = model_df.dropna(axis=0, how="any").reset_index(drop=True)

    clean.to_csv(PROCESSED_DIR / "df_asst_bnk_ecb_clean_full.csv", index=False)
    model_df.to_csv(OUTPUT_CSV, index=False)

    print(f"Raw rows: {len(raw)}")
    print(f"Clean full rows: {len(clean)}")
    print(f"Model-ready rows after dropping NaNs: {len(model_df)}")
    print(f"Model-ready columns: {len(model_df.columns)}")
    print(f"Saved full cleaned file: {PROCESSED_DIR / 'df_asst_bnk_ecb_clean_full.csv'}")
    print(f"Saved model-ready file: {OUTPUT_CSV}")
    print("\nModel-ready missing values per column before drop:")
    print(clean[numeric_cols].isna().sum().to_string())


if __name__ == "__main__":
    main()
