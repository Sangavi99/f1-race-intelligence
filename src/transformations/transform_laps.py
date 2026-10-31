from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "barcelona_2026_laps_clean.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "barcelona_2026_laps_transformed.csv"
)


def transform_laps() -> None:
    """Transform cleaned F1 lap data into analytics-ready data."""

    df = pd.read_csv(INPUT_FILE)

    original_count = len(df)

    # Convert lap times into seconds.
    df["LapTimeSeconds"] = (
        pd.to_timedelta(df["LapTime"], errors="coerce")
        .dt.total_seconds()
    )

    # Convert lap numbers into integers.
    df["LapNumber"] = pd.to_numeric(
        df["LapNumber"], errors="coerce"
    )

    # Convert tyre age into numeric values.
    df["TyreLife"] = pd.to_numeric(
        df["TyreLife"], errors="coerce"
    )

    # Sort laps by driver and lap number.
    df = df.sort_values(
        ["Driver", "LapNumber"]
    ).reset_index(drop=True)

    # Calculate each driver's previous lap time.
    df["PreviousLapTimeSeconds"] = (
        df.groupby("Driver")["LapTimeSeconds"].shift(1)
    )

    # Calculate the difference from the previous lap.
    df["LapTimeDeltaSeconds"] = (
        df["LapTimeSeconds"]
        - df["PreviousLapTimeSeconds"]
    )

    # Save the transformed dataset.
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False)

    print("F1 LAP DATA TRANSFORMATION")
    print("==========================")
    print(f"Input records: {original_count}")
    print(f"Output records: {len(df)}")
    print(f"Output file: {OUTPUT_FILE}")
    print("\nSample transformed data:")

    print(
        df[
            [
                "Driver",
                "LapNumber",
                "LapTimeSeconds",
                "PreviousLapTimeSeconds",
                "LapTimeDeltaSeconds",
                "Compound",
                "TyreLife",
            ]
        ].head(10).to_string(index=False)
    )


if __name__ == "__main__":
    transform_laps()
