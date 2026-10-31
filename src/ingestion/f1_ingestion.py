
from pathlib import Path

import fastf1
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data" / "raw"

YEAR = 2026
GRAND_PRIX = "Barcelona Grand Prix"
SESSION_TYPE = "R"


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    cache_dir = PROJECT_ROOT / "data" / "fastf1_cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    fastf1.Cache.enable_cache(str(cache_dir))

    print(f"Loading {YEAR} {GRAND_PRIX} race data...")

    session = fastf1.get_session(YEAR, GRAND_PRIX, SESSION_TYPE)
    session.load(
        laps=True,
        telemetry=False,
        weather=False,
        messages=False,
    )

    laps: pd.DataFrame = session.laps.copy()

    if laps.empty:
        raise ValueError("No lap data was returned for this session.")

    output_file = DATA_DIR / "barcelona_2026_laps.csv"
    laps.to_csv(output_file, index=False)

    print(f"Successfully saved {len(laps)} lap records.")
    print(f"Output file: {output_file}")
    print(laps[["Driver", "LapNumber", "LapTime"]].head())


if __name__ == "__main__":
    main()
