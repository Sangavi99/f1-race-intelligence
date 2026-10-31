from pyexpat import errors

import pandas as pd
import argparse
import logging
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOG_DIR / "validation.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def validate_laps(file_path: str) -> bool:
    """Check the quality of an F1 lap-data CSV."""

    try:
       df = pd.read_csv(file_path)

       logger.info(f"Successfully loaded dataset: {file_path}")
       logger.info(f"Total records: {len(df)}")
       logger.info(f"Total columns: {len(df.columns)}")

    except FileNotFoundError:
       logger.error(f"File not found: {file_path}")
       return False

    except pd.errors.EmptyDataError:
       logger.error("The CSV file is empty.")
       return False

    except pd.errors.ParserError:
       logger.error("Unable to read the CSV file. File format may be incorrect.")
       return False

    except Exception as e:
       logger.error(f"Unexpected problem: {e}")
       return False

    errors = []
    warnings = []

    if df.empty:
        logger.error("Validation FAILED: Dataset is empty.")
        return False

    required_columns = [
        "Driver",
        "LapNumber",
        "LapTime",
        "Team",
    ]

    # Check 1: Required columns
    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        errors.append(
            f"Missing required columns: {missing_columns}"
        )

    # Run data checks only when required columns exist.
    if not missing_columns:

        # Check 2A: LapNumber data type
        if not pd.api.types.is_numeric_dtype(df["LapNumber"]):
            errors.append(
                f"LapNumber must be numeric, found {df['LapNumber'].dtype}."
            )
        # Check 2B: LapTime format
        converted_lap_times = pd.to_timedelta(
            df["LapTime"],
            errors="coerce"
        )

        invalid_lap_times = (
            converted_lap_times.isna()
            & df["LapTime"].notna()
        )

        if invalid_lap_times.any():
            errors.append(
                f"Found {invalid_lap_times.sum()} invalid lap times."
            )

        # Check 2C: LapTime must be positive
        non_positive_lap_times = (
            converted_lap_times <= pd.Timedelta(0)
        )

        if non_positive_lap_times.any():
            errors.append(
                f"Found {non_positive_lap_times.sum()} "
                "zero or negative lap times."
            )

        # Check 2D: TyreLife data type
        if "TyreLife" in df.columns:
            if not pd.api.types.is_numeric_dtype(df["TyreLife"]):
                errors.append(
                    f"TyreLife must be numeric, found {df['TyreLife'].dtype}."
                )
        # Check 2D-1: TyreLife must not be negative
        if (
            "TyreLife" in df.columns
            and pd.api.types.is_numeric_dtype(df["TyreLife"])
        ):
            invalid_tyre_life = df["TyreLife"] < 0

            if invalid_tyre_life.any():
                errors.append(
                    f"Found {invalid_tyre_life.sum()} negative TyreLife values."
                )        

        # Check: LapTime must be positive
        valid_lap_times = converted_lap_times.dropna()

        if (valid_lap_times <= pd.Timedelta(0)).any():
            errors.append("LapTime contains zero or negative values.")

        # Check 2E: Driver and Team values
        for column in ["Driver", "Team"]:
            if df[column].isna().any() or (df[column].astype(str).str.strip() == "").any():
                errors.append(
                    f"{column} contains missing or empty values."
                )

        # Check 2F: LapNumber must be positive
        if (df["LapNumber"] <= 0).any():
            errors.append("LapNumber contains zero or negative values.")        

        # Check 2: Empty dataset
        if df.empty:
            errors.append("Dataset is empty.")

        # Check 3: Duplicate records
        if df.duplicated().any():
            errors.append(
                f"Found {df.duplicated().sum()} duplicate rows."
            )
	    # Check 3B: Duplicate driver-lap pairs
        duplicate_rows = df[
            df.duplicated(subset=["Driver", "LapNumber"], keep=False)
        ]

        duplicate_driver_laps = len(duplicate_rows)

        if duplicate_driver_laps > 0:
           errors.append(
               f"Found {duplicate_driver_laps} rows with duplicate driver-lap pairs."
           )

        # Check 4: Invalid lap numbers
        invalid_laps = (
            df["LapNumber"].isna()
            | (df["LapNumber"] <= 0)
        )

        if invalid_laps.any():
            errors.append(
                f"Found {invalid_laps.sum()} invalid lap numbers."
            )

        # Check 5: Missing lap times
        missing_times = df["LapTime"].isna().sum()

        if missing_times:
            errors.append(
                f"Found {missing_times} missing lap times."
            )

        # Check 6: Missing sector timings
        for column in [
            "Sector1Time",
            "Sector2Time",
            "Sector3Time",
        ]:
            if column in df.columns:
                count = df[column].isna().sum()

                if count:
                    warnings.append(
                        f"{column}: {count} missing values."
                    )

        # Check 7: Entirely empty columns
        empty_columns = [
            column
            for column in df.columns
            if df[column].isna().all()
        ]

        if empty_columns:
            warnings.append(
                f"Entirely empty columns: {empty_columns}"
            )

    logger.info("\nF1 LAP DATA QUALITY REPORT")
    logger.info("=" * 30)
    logger.info(f"Total records: {len(df)}")
    logger.info(f"Total columns: {len(df.columns)}")

    logger.info("\nMISSING VALUE SUMMARY")
    missing_counts = df.isna().sum()
    missing_counts = missing_counts[missing_counts > 0]

    for column, count in missing_counts.items():
        percentage = count / len(df) * 100
        logger.info(
            f"{column}: {count} missing "
            f"({percentage:.2f}%)"
        )

    logger.info("\nDUPLICATE DRIVER-LAP CHECK")
    logger.info(f"Duplicate driver-lap pairs: {duplicate_driver_laps}")
    logger.info("\nERRORS")

    for error in errors:
        logger.error(f"- {error}")

    if not errors:
        logger.info("None")

    logger.info("\nWARNINGS")
    for warning in warnings:
        logger.warning(f"- {warning}")

    if not warnings:
        logger.info("None")

    passed = not errors

    logger.info("\nVALIDATION STATUS:")
    logger.info("PASSED" if passed else "FAILED")

    return passed


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Validate F1 lap data"
    )
    parser.add_argument(
        "file_path",
        help="Path to the F1 lap CSV file"
    )

    args = parser.parse_args()
    validate_laps(args.file_path)
