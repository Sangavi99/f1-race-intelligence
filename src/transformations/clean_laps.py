from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_FILE = PROJECT_ROOT / "data" / "raw" / "barcelona_2026_laps.csv"
OUTPUT_FILE = PROJECT_ROOT / "data" / "processed" / "barcelona_2026_laps_clean.csv"


def clean_laps() -> None:
    df = pd.read_csv(RAW_FILE)

    original_count = len(df)

    # Keep a separate copy containing only rows with lap times.
    clean_df = df.dropna(subset=["LapTime"]).copy()

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    clean_df.to_csv(OUTPUT_FILE, index=False)

    print("F1 LAP DATA CLEANING")
    print("--------------------")
    print(f"Original records: {original_count}")
    print(f"Clean records: {len(clean_df)}")
    print(f"Records excluded: {original_count - len(clean_df)}")
    print(f"Output file: {OUTPUT_FILE}")


if __name__ == "__main__":
    clean_laps()
