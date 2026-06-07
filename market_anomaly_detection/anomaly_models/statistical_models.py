"""
Statistical anomaly detection models
"""

import numpy as np
import pandas as pd
from typing import Tuple
from market_anomaly_detection.base.interfaces import BaseAnomalyDetector


class ZScoreDetector(BaseAnomalyDetector):
    """Z-score based anomaly detection"""

    def __init__(self, threshold: int = 3, window: int = 30, target_col_idx: int = None):
        """Set Z-score threshold and rolling window size."""
        super().__init__("ZScoreDetector")
        self.threshold = threshold
        self.window = window
        self.target_col_idx = target_col_idx

    def fit(self, data: np.ndarray) -> "ZScoreDetector":
        """Z-score doesn't require fitting"""
        self.is_fitted = True
        return self

    def detect(self, data: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Detect anomalies using rolling Z-score or precomputed flags"""
        self._validate_fitted()

        if hasattr(self, "precomputed_flags") and self.precomputed_flags is not None:
            return self.precomputed_flags, self.precomputed_scores

        # Handle multi-variate data
        if data.ndim == 1:
            data = data.reshape(-1, 1)

        n_samples = data.shape[0]
        scores = np.zeros(n_samples)

        # Compute Z-score for each feature and take max across features
        if self.target_col_idx is not None:
            col_indices = [self.target_col_idx]
        else:
            col_indices = range(data.shape[1])

        for col_idx in col_indices:
            series = pd.Series(data[:, col_idx])
            rolling_mean = series.rolling(window=self.window).mean()
            rolling_std = series.rolling(window=self.window).std()
            z_scores = np.abs((series - rolling_mean) / (rolling_std + 1e-8))
            scores = np.maximum(scores, z_scores.values)

        flags = (scores >= self.threshold).astype(int)

        scores = np.nan_to_num(scores, nan=0.0)
        flags = np.nan_to_num(flags, nan=0)

        return flags, scores


class IQRDetector(BaseAnomalyDetector):
    """IQR-based anomaly detection"""

    def __init__(self, window: int = 30, multiplier: float = 1.5, feature_indices: list = None):
        """Set rolling window size and IQR multiplier."""
        super().__init__("IQRDetector")
        self.window = window
        self.multiplier = multiplier
        self.feature_indices = feature_indices

    def fit(self, data: np.ndarray) -> "IQRDetector":
        """IQR doesn't require fitting"""
        self.is_fitted = True
        return self

    def detect(self, data: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Detect anomalies using rolling IQR or precomputed flags"""
        self._validate_fitted()

        if hasattr(self, "precomputed_flags") and self.precomputed_flags is not None:
            return self.precomputed_flags, self.precomputed_scores

        # Handle multi-variate data
        if data.ndim == 1:
            data = data.reshape(-1, 1)

        n_samples = data.shape[0]
        scores = np.zeros(n_samples)
        flags_all = np.zeros(n_samples, dtype=int)

        # Compute IQR for each feature
        if self.feature_indices is not None:
            col_indices = self.feature_indices
        else:
            col_indices = range(data.shape[1])

        for col_idx in col_indices:
            series = pd.Series(data[:, col_idx])
            q1 = series.rolling(window=self.window).quantile(0.25)
            q3 = series.rolling(window=self.window).quantile(0.75)
            iqr = q3 - q1

            lower_bound = q1 - self.multiplier * iqr
            upper_bound = q3 + self.multiplier * iqr

            col_flags = ((series < lower_bound) | (series > upper_bound)).astype(int).values
            col_scores = np.maximum(lower_bound - series, series - upper_bound).values
            col_scores = np.maximum(col_scores, 0)

            scores = np.maximum(scores, col_scores)
            flags_all = np.maximum(flags_all, col_flags)

        scores = np.nan_to_num(scores, nan=0.0)
        flags_all = np.nan_to_num(flags_all, nan=0)

        return flags_all, scores
