import pandas as pd
import pytest

from market_anomaly_detection.data_processing.processor import DataProcessor


def test_validate_schema_missing_columns_raises():
    """Ensure missing required columns trigger validation errors."""
    df = pd.DataFrame({
        "quote_datetime": ["2024-01-01"],
        "open": [1.0],
        "high": [1.1],
        "low": [0.9],
        "close": [1.0],
        "bid": [0.99],
        "mid": [1.0],
        "vwap": [1.0],
    })

    processor = DataProcessor(required_columns=["quote_datetime", "ask"])

    with pytest.raises(ValueError, match="Missing required columns"):
        processor.calculate(df)
