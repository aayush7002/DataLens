import argparse
from pathlib import Path

import pandas as pd


def main():
    parser = argparse.ArgumentParser(
        description="DataLens - Automated CSV Data Quality Profiler"
    )
    
    parser.add_argument(
        "csv_file",
        nargs="?",
        help="Path to the CSV file to analyze"
    )

    parser.add_argument(
        "--report",
        help="Optional path for saving the generated report"
    )

    args = parser.parse_args()

    filename = args.csv_file

    if not filename:
        filename = input("Enter the path to a CSV file: ").strip()

    try:
        data = load_data(filename)

        report = generate_report(data, filename)

        print()
        print(report)

        if args.report:
            Path(args.report).write_text(report, encoding="utf-8")
            print(f"\nReport saved to: {args.report}")

    except (FileNotFoundError, ValueError, pd.errors.ParserError) as error:
        print(f"Error: {error}")


def load_data(filename):
    """
    Load and validate a CSV file.

    Returns a pandas DataFrame.
    """

    path = Path(filename)

    if not path.exists():
        raise FileNotFoundError(f"{filename} does not exist.")

    if path.suffix.lower() != ".csv":
        raise ValueError("DataLens currently supports CSV files only.")

    data = pd.read_csv(path)

    if data.empty:
        raise ValueError("The CSV file contains no rows.")

    return data


def find_missing_values(data):
    """
    Return missing-value statistics for each column.

    Example:
    {
        "age": {
            "count": 2,
            "percent": 20.0
        }
    }
    """

    result = {}

    total_rows = len(data)

    for column in data.columns:
        count = int(data[column].isna().sum())

        if total_rows == 0:
            percent = 0
        else:
            percent = (count / total_rows) * 100

        result[column] = {
            "count": count,
            "percent": round(percent, 2)
        }

    return result


def find_duplicates(data):
    """
    Return the number of completely duplicated rows.
    """

    return int(data.duplicated().sum())


def detect_outliers(data):
    """
    Detect numeric outliers using the IQR method.

    A value is considered an outlier when it falls below:

        Q1 - 1.5 * IQR

    or above:

        Q3 + 1.5 * IQR
    """

    results = {}

    numeric_columns = data.select_dtypes(include="number").columns

    for column in numeric_columns:
        values = data[column].dropna()

        # Very small datasets are not useful for IQR detection.
        if len(values) < 4:
            results[column] = 0
            continue

        q1 = values.quantile(0.25)
        q3 = values.quantile(0.75)

        iqr = q3 - q1

        lower_bound = q1 - (1.5 * iqr)
        upper_bound = q3 + (1.5 * iqr)

        outliers = values[
            (values < lower_bound) |
            (values > upper_bound)
        ]

        results[column] = int(len(outliers))

    return results


def calculate_quality_score(data):
    """
    Calculate a simple data-quality score from 0 to 100.

    Score weighting:

    50% completeness
    30% uniqueness
    20% lack of numeric outliers

    This is a heuristic rather than an industry standard.
    """

    rows = len(data)
    columns = len(data.columns)

    if rows == 0 or columns == 0:
        return 0.0

    # -------------------------
    # Completeness
    # -------------------------

    total_cells = rows * columns
    missing_cells = int(data.isna().sum().sum())

    completeness = 1 - (missing_cells / total_cells)

    # -------------------------
    # Uniqueness
    # -------------------------

    duplicates = find_duplicates(data)

    uniqueness = 1 - (duplicates / rows)

    # -------------------------
    # Outlier quality
    # -------------------------

    outliers = detect_outliers(data)
    total_outliers = sum(outliers.values())

    numeric_columns = data.select_dtypes(include="number")

    numeric_cells = int(numeric_columns.notna().sum().sum())

    if numeric_cells == 0:
        outlier_quality = 1
    else:
        outlier_rate = total_outliers / numeric_cells
        outlier_quality = 1 - outlier_rate

    # -------------------------
    # Weighted score
    # -------------------------

    score = (
        completeness * 0.50
        + uniqueness * 0.30
        + outlier_quality * 0.20
    ) * 100

    # Keep result between 0 and 100.
    score = max(0, min(100, score))

    return round(score, 2)


def profile_columns(data):
    """
    Generate useful statistics for every column.
    """

    profiles = {}

    for column in data.columns:
        series = data[column]

        profile = {
            "type": str(series.dtype),
            "missing": int(series.isna().sum()),
            "unique": int(series.nunique(dropna=True))
        }

        if pd.api.types.is_numeric_dtype(series):
            clean = series.dropna()

            if not clean.empty:
                profile["min"] = clean.min()
                profile["max"] = clean.max()
                profile["mean"] = round(float(clean.mean()), 2)

        profiles[column] = profile

    return profiles


def generate_report(data, filename="Dataset"):
    """
    Generate a human-readable data quality report.
    """

    missing = find_missing_values(data)
    duplicates = find_duplicates(data)
    outliers = detect_outliers(data)
    profiles = profile_columns(data)
    score = calculate_quality_score(data)

    total_missing = sum(
        information["count"]
        for information in missing.values()
    )

    lines = []

    lines.append("=" * 60)
    lines.append("DATALENS - AUTOMATED CSV DATA QUALITY REPORT")
    lines.append("=" * 60)

    lines.append(f"File: {filename}")
    lines.append(f"Rows: {len(data)}")
    lines.append(f"Columns: {len(data.columns)}")
    lines.append(f"Missing cells: {total_missing}")
    lines.append(f"Duplicate rows: {duplicates}")
    lines.append(f"Data Quality Score: {score}/100")

    lines.append("")
    lines.append("-" * 60)
    lines.append("MISSING VALUES")
    lines.append("-" * 60)

    has_missing = False

    for column, information in missing.items():

        if information["count"] > 0:
            has_missing = True

            lines.append(
                f"{column}: "
                f"{information['count']} "
                f"({information['percent']}%)"
            )

    if not has_missing:
        lines.append("No missing values detected.")

    lines.append("")
    lines.append("-" * 60)
    lines.append("OUTLIERS")
    lines.append("-" * 60)

    if not outliers:
        lines.append("No numeric columns detected.")

    else:
        has_outliers = False

        for column, count in outliers.items():
            if count > 0:
                has_outliers = True
                lines.append(f"{column}: {count}")

        if not has_outliers:
            lines.append("No numeric outliers detected.")

    lines.append("")
    lines.append("-" * 60)
    lines.append("COLUMN PROFILE")
    lines.append("-" * 60)

    for column, information in profiles.items():

        lines.append("")
        lines.append(f"Column: {column}")
        lines.append(f"  Type: {information['type']}")
        lines.append(f"  Missing: {information['missing']}")
        lines.append(f"  Unique values: {information['unique']}")

        if "min" in information:
            lines.append(f"  Minimum: {information['min']}")
            lines.append(f"  Maximum: {information['max']}")
            lines.append(f"  Mean: {information['mean']}")

    lines.append("")
    lines.append("=" * 60)

    return "\n".join(lines)


if __name__ == "__main__":
    main()