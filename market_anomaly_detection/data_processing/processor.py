"""
Data loading and processing module
"""

import logging
import pandas as pd
import numpy as np
from pathlib import Path
from typing import List
from market_anomaly_detection.base.interfaces import BaseFeatureCalculator


class DataLoader:
    """Handles data loading and basic validation"""

    def __init__(self, csv_path: Path, logger: logging.Logger | None = None):
        """Store data source path and logger."""
        self.csv_path = csv_path
        self.logger = logger or logging.getLogger(__name__)
        self.data = None
        self.original_shape = None

    def load(self) -> pd.DataFrame:
        """Load data from CSV"""
        self.data = pd.read_csv(self.csv_path)
        self.original_shape = self.data.shape
        self.logger.info("Loaded data: %s", self.original_shape)
        return self.data

    def get_data(self) -> pd.DataFrame:
        """Get loaded data"""
        if self.data is None:
            raise ValueError("Data not loaded. Call load() first.")
        return self.data


class DataProcessor(BaseFeatureCalculator):
    """Data preprocessing and quality checks"""

    def __init__(
        self,
        required_columns: List[str] | None = None,
        missing_value_strategy: str = "drop",
        logger: logging.Logger | None = None,
    ):
        """Initialize processor configuration and logger."""
        super().__init__("DataProcessor")
        self.required_columns = required_columns or []
        self.missing_value_strategy = missing_value_strategy
        self.logger = logger or logging.getLogger(__name__)
        self.quality_report = {}

    def validate_schema(self, data: pd.DataFrame) -> None:
        """Validate required columns exist."""
        if not self.required_columns:
            return
        missing = [col for col in self.required_columns if col not in data.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")

    def validate_and_clean_price_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """Validate and clean price data consistency"""
        df = data.copy()
        issues = {}

        # Keep chronological order before return-based checks
        if "quote_datetime" in df.columns:
            df["quote_datetime"] = pd.to_datetime(df["quote_datetime"], errors="coerce")
            df = df.sort_values("quote_datetime").reset_index(drop=True)

        # Check 1: Non-positive OHLC -> drop rows
        price_cols = [c for c in ["open", "high", "low", "close"] if c in df.columns]
        if price_cols:
            invalid_price_mask = (df[price_cols] <= 0).any(axis=1)
            issues["invalid_prices"] = int(invalid_price_mask.sum())
            if issues["invalid_prices"] > 0:
                df = df.loc[~invalid_price_mask].reset_index(drop=True)

        # Check 2a: High < Low -> swap
        if "high" in df.columns and "low" in df.columns:
            high_lt_low_mask = df["high"] < df["low"]
            issues["high_lt_low"] = int(high_lt_low_mask.sum())
            if issues["high_lt_low"] > 0:
                tmp_low = df.loc[high_lt_low_mask, "low"].copy()
                df.loc[high_lt_low_mask, "low"] = df.loc[high_lt_low_mask, "high"]
                df.loc[high_lt_low_mask, "high"] = tmp_low

        # Check 2b: Close outside [Low, High] -> clip
        if all(c in df.columns for c in ["close", "low", "high"]):
            close_outside_mask = (df["close"] < df["low"]) | (df["close"] > df["high"])
            issues["close_outside"] = int(close_outside_mask.sum())
            if issues["close_outside"] > 0:
                df.loc[close_outside_mask, "close"] = df.loc[close_outside_mask, "close"].clip(
                    lower=df.loc[close_outside_mask, "low"],
                    upper=df.loc[close_outside_mask, "high"],
                )

        # Check 2c: Open outside [Low, High] -> clip
        if all(c in df.columns for c in ["open", "low", "high"]):
            open_outside_mask = (df["open"] < df["low"]) | (df["open"] > df["high"])
            issues["open_outside"] = int(open_outside_mask.sum())
            if issues["open_outside"] > 0:
                df.loc[open_outside_mask, "open"] = df.loc[open_outside_mask, "open"].clip(
                    lower=df.loc[open_outside_mask, "low"],
                    upper=df.loc[open_outside_mask, "high"],
                )

        # Check 3: Bid > Ask -> set to Mid
        if "bid" in df.columns and "ask" in df.columns:
            bid_gt_ask_mask = df["bid"] > df["ask"]
            issues["bid_gt_ask"] = int(bid_gt_ask_mask.sum())
            if issues["bid_gt_ask"] > 0:
                if "mid" in df.columns:
                    mid_vals = df.loc[bid_gt_ask_mask, "mid"]
                    df.loc[bid_gt_ask_mask, "bid"] = mid_vals.values
                    df.loc[bid_gt_ask_mask, "ask"] = mid_vals.values
                else:
                    tmp_ask = df.loc[bid_gt_ask_mask, "ask"].copy()
                    df.loc[bid_gt_ask_mask, "ask"] = df.loc[bid_gt_ask_mask, "bid"]
                    df.loc[bid_gt_ask_mask, "bid"] = tmp_ask

        # Check 4: Duplicate timestamps -> keep first
        if "quote_datetime" in df.columns:
            dups = df.duplicated(subset=["quote_datetime"])
            issues["duplicates"] = int(dups.sum())
            if issues["duplicates"] > 0:
                df = df.drop_duplicates(subset=["quote_datetime"], keep="first").reset_index(
                    drop=True
                )

        # Check 5: Negative volume -> set to 0
        if "trade_volume" in df.columns:
            neg_vol_mask = df["trade_volume"] < 0
            issues["negative_volume"] = int(neg_vol_mask.sum())
            if issues["negative_volume"] > 0:
                df.loc[neg_vol_mask, "trade_volume"] = 0

        # Check 6: Extreme single-bar returns (>20%) -> drop rows
        if "close" in df.columns:
            returns = df["close"].pct_change()
            extreme_mask = returns.abs() > 0.20
            issues["extreme_returns"] = int(extreme_mask.sum())
            if issues["extreme_returns"] > 0:
                df = df.loc[~extreme_mask].reset_index(drop=True)

        self.quality_report = issues
        return df

    def handle_missing_values(self, data: pd.DataFrame, strategy: str = "drop") -> pd.DataFrame:
        """Handle missing values"""
        if strategy == "drop":
            return data.dropna()
        elif strategy == "forward_fill":
            return data.fillna(method="ffill")
        else:
            return data

    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        """Main processing pipeline"""
        # Copy to avoid modifying original
        df = data.copy()

        # Schema validation
        self.validate_schema(df)

        # Handle missing values
        df = self.handle_missing_values(df, strategy=self.missing_value_strategy)

        # Validate and clean price data
        df = self.validate_and_clean_price_data(df)

        self.logger.info("Data quality report: %s", self.quality_report)
        return df


class FinancialMetricsCalculator(BaseFeatureCalculator):
    """Calculate financial metrics"""

    def __init__(self):
        """Initialize the metrics calculator."""
        super().__init__("FinancialMetricsCalculator")

    def calculate_returns(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate return metrics"""
        df = data.copy()

        # Intra-hour returns
        df["return_1h"] = df["close"].pct_change()
        df["log_return"] = np.log(df["close"] / df["close"].shift(1))

        # Absolute high-low range
        df["high_low_range"] = (df["high"] - df["low"]) / df["close"]

        return df

    def calculate_volatility(
        self, data: pd.DataFrame, windows: List[int] = [6, 24]
    ) -> pd.DataFrame:
        """Calculate rolling volatility"""
        df = data.copy()

        for window in windows:
            col_name = f"vol_{window}h"
            df[col_name] = df["log_return"].rolling(window=window).std()

        return df

    def calculate_spread_metrics(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate spread-based metrics"""
        df = data.copy()

        if "bid" in df.columns and "ask" in df.columns:
            df["spread"] = df["ask"] - df["bid"]
            df["spread_pct"] = df["spread"] / df["mid"]

        if "vwap" in df.columns:
            df["vwap_deviation"] = (df["close"] - df["vwap"]) / df["vwap"]

        return df

    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate all financial metrics"""
        df = data.copy()
        df = self.calculate_returns(df)
        df = self.calculate_volatility(df)
        df = self.calculate_spread_metrics(df)
        return df
