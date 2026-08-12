"""
Cricket AI Analytics - Data Ingestion
Downloads ball-by-ball cricket data from Cricsheet and prepares DataFrames.
"""

import requests
import pandas as pd
import zipfile
import io
import json
import glob
import os

CRICSHEET_URL = "https://cricsheet.org/downloads/all_json.zip"
RAW_DIR = "data/raw"


def download_cricsheet_data(url=CRICSHEET_URL, dest=RAW_DIR):
    """Download and extract Cricsheet ball-by-ball JSON data."""
    print(f"[ingest] Downloading Cricsheet data from {url} ...")
    os.makedirs(dest, exist_ok=True)
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    print(f"[ingest] Downloaded {len(response.content) / 1024 / 1024:.2f} MB, extracting...")

    with zipfile.ZipFile(io.BytesIO(response.content)) as z:
        z.extractall(dest)

    print(f"[ingest] Extracted {len(z.namelist())} files to {dest}")
    return dest


def load_matches_to_dataframe(raw_dir=RAW_DIR):
    """Load JSON files into a single DataFrame with proper over/ball parsing."""
    print(f"[ingest] Loading matches from {raw_dir} ...")
    records = []
    json_files = glob.glob(os.path.join(raw_dir, "*.json"))
    print(f"[ingest] Found {len(json_files)} JSON files, sampling 20 for dev")

    for jf in json_files[:20]:
        with open(jf, "r") as f:
            data = json.load(f)
            for inning in data.get("innings", []):
                for over_data in inning.get("overs", []):
                    over_num = over_data.get("over")
                    for delivery in over_data.get("deliveries", []):
                        over_str = f"{over_num}.{delivery.get('ball', 1)}"
                        records.append({
                            "match_id": os.path.basename(jf),
                            "over": over_str,
                            "batter": delivery.get("batter"),
                            "bowler": delivery.get("bowler"),
                            "runs": delivery.get("runs", {}).get("total", 0),
                            "innings": inning.get("inning", 1),
                        })

    df = pd.DataFrame(records)
    print(f"[ingest] Raw DataFrame created with {len(df)} rows")

    # FIX: handle decimal overs like "1.1" by splitting on '.' with pandas
    # Previous bug: int("1.1") -> ValueError
    df[["over_num", "ball_num"]] = df["over"].astype(str).str.split(".", expand=True)
    df["over_num"] = df["over_num"].astype(int)
    df["ball_num"] = df["ball_num"].astype(int)
    print(f"[ingest] Parsed overs/balls for {len(df)} deliveries (over_num, ball_num)")
    print("[ingest] Decimal over parsing fixed with pandas str.split")

    return df


if __name__ == "__main__":
    print("[ingest] Starting ingestion pipeline...")
    download_cricsheet_data()
    df = load_matches_to_dataframe()
    print(df.head())
    print(f"[ingest] Successfully loaded {len(df)} deliveries")
    print("[ingest] Done.")
