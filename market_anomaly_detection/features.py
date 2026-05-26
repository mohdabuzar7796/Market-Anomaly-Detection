"""Feature engineering utilities."""

import pandas as pd
from market_anomaly_detection.data.processor import DataProcessor, FinancialMetricsCalculator


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """Validate and enrich data with engineered features."""
    processor = DataProcessor()
    metrics = FinancialMetricsCalculator()
    df_processed = processor.calculate(df)
    return metrics.calculate(df_processed)
