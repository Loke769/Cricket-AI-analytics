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

CRICSHEET_URL = "https://cricsheet.org/downloads/all_json.zip"
RAW_DIR = "data/raw"


def download_cricsheet_data(url=CRICSHEET_URL, dest=RAW_DIR):
    """Download and extract Cricsheet ball-by-ball JSON data."""
    print(f"Downloading Cricsheet data from {url} ...")
    response = requests.get(url, timeout=30)
    response.raise_for_status()

    with zipfile.ZipFile(io.BytesIO(response.content)) as z:
        z.extractall(dest)

    print(f"Extracted files to {dest}")
    return dest


def load_matches_to_dataframe(raw_dir=RAW_DIR):
    """Load JSON files into a single DataFrame."""
    import os

    records = []
    json_files = glob.glob(os.path.join(raw_dir, "*.json"))
    for jf in json_files[:20]:  # sample first 20 files for dev
        with open(jf, "r") as f:
            data = json.load(f)
            for inning in data.get("innings", []):
                for over_data in inning.get("overs", []):
                    over_num = over_data.get("over")
                    for delivery in over_data.get("deliveries", []):
                        # Cricsheet overs like 0.1, 1.1, 19.5 — store as decimal string
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

    # BUG: ValueError when over column has decimal format like "1.1"
    # int("1.1") raises: ValueError: invalid literal for int() with base 10: '1.1'
    df["over"] = df["over"].apply(lambda x: int(x))

    return df


if __name__ == "__main__":
    download_cricsheet_data()
    df = load_matches_to_dataframe()
    print(df.head())
    print(f"Loaded {len(df)} deliveries")
