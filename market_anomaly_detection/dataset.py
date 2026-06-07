"""Dataset utilities for loading raw market data."""

from pathlib import Path
import pandas as pd
from market_anomaly_detection.data_processing.processor import DataLoader


def load_raw_data(csv_path: Path | str) -> pd.DataFrame:
    """Load raw CSV data into a DataFrame."""
    loader = DataLoader(Path(csv_path))
    return loader.load()
