import pandas as pd
import pytest

from project import (
    find_missing_values,
    find_duplicates,
    detect_outliers,
    calculate_quality_score,
)


def test_find_missing_values():

    data = pd.DataFrame({
        "name": ["Alice", "Bob", None, "David"],
        "age": [20, None, 22, 23]
    })

    result = find_missing_values(data)

    assert result["name"]["count"] == 1
    assert result["name"]["percent"] == 25.0

    assert result["age"]["count"] == 1
    assert result["age"]["percent"] == 25.0


def test_find_duplicates():

    data = pd.DataFrame({
        "name": ["Alice", "Bob", "Alice"],
        "age": [20, 22, 20]
    })

    assert find_duplicates(data) == 1


def test_detect_outliers():

    data = pd.DataFrame({
        "salary": [50000, 51000, 52000, 53000, 500000]
    })

    result = detect_outliers(data)

    assert result["salary"] == 1


def test_calculate_quality_score():

    clean_data = pd.DataFrame({
        "name": ["Alice", "Bob", "Charlie"],
        "age": [20, 21, 22]
    })

    score = calculate_quality_score(clean_data)

    assert score == pytest.approx(100.0)