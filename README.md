# DataLens

**Automated data-quality profiler for CSV files.** Point DataLens at any CSV and it produces a report with a **0–100 Data Quality Score**, plus a breakdown of missing values, duplicate rows, numeric outliers, and per-column statistics.

Bad data quietly breaks analyses and machine learning models. DataLens gives a quick first look at how trustworthy a dataset is before you use it.

## Features

- **Missing values:** count and percentage of empty cells in every column
- **Duplicate rows:** number of rows that are exact copies of another row
- **Outlier detection:** flags numeric values outside the IQR range (below Q1 − 1.5·IQR or above Q3 + 1.5·IQR)
- **Column profiling:** data type, unique values, and min / max / mean for numeric columns
- **Quality score:** a single 0–100 score combining the checks above
- **Report export:** optionally saves the report to a text file

## How the score works

The score is a weighted combination of three checks:

| Component | Weight | What it measures |
|---|---|---|
| Completeness | 50% | Share of cells that are not missing |
| Uniqueness | 30% | Share of rows that are not duplicates |
| Outlier quality | 20% | Share of numeric values that are not IQR outliers |

```
score = (0.50 × completeness + 0.30 × uniqueness + 0.20 × outlier_quality) × 100
```

This is a practical heuristic, not an industry standard. The weights reflect that missing data usually does the most damage.

## Installation

```bash
git clone https://github.com/aayush7002/DataLens.git
cd DataLens
pip install -r requirements.txt
```

Requires Python 3.9+.

## Usage

```bash
# Analyze a CSV and print the report
python project.py sample_data.csv

# Analyze and also save the report to a file
python project.py sample_data.csv --report report.txt

# Run with no arguments to be prompted for a file path
python project.py
```

## Example

Running DataLens on the included `sample_data.csv` (8 rows, 5 columns):

```
============================================================
DATALENS - AUTOMATED CSV DATA QUALITY REPORT
============================================================
File: sample_data.csv
Rows: 8
Columns: 5
Missing cells: 2
Duplicate rows: 1
Data Quality Score: 92.42/100

------------------------------------------------------------
MISSING VALUES
------------------------------------------------------------
age: 1 (12.5%)
email: 1 (12.5%)

------------------------------------------------------------
OUTLIERS
------------------------------------------------------------
salary: 1
```

DataLens catches the missing age and email, the duplicated "Alice" row, and the $900,000 salary that doesn't fit the rest of the column. The full report, including the column profile, is in `report.txt`.

## Testing

```bash
pytest test_project.py
```

The tests cover missing-value detection, duplicate detection, outlier detection, and the quality score.

## Project structure

```
project.py          # DataLens CLI and analysis functions
test_project.py     # pytest unit tests
sample_data.csv     # Example dataset with deliberate quality issues
report.txt          # Example output report
requirements.txt    # Dependencies (pandas, pytest)
```

## Future improvements

- Validate formats such as emails, dates, and phone numbers
- Detect mixed data types within a column
- Let users adjust the score weights
- Support Excel and JSON files
