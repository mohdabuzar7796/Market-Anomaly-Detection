"""
Machine learning anomaly detection models
"""

import numpy as np
from typing import Tuple
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from market_anomaly_detection.base.interfaces import BaseAnomalyDetector


class IsolationForestDetector(BaseAnomalyDetector):
    """Isolation Forest based anomaly detection"""

    def __init__(
        self,
        n_estimators: int = 200,
        contamination: float = 0.01,
        random_state: int = 42,
    ):
        """Configure Isolation Forest hyperparameters."""
        super().__init__("IsolationForestDetector")
        self.n_estimators = n_estimators
        self.contamination = contamination
        self.random_state = random_state
        self.model = IsolationForest(
            n_estimators=n_estimators,
            contamination=contamination,
            random_state=random_state,
            n_jobs=-1,
        )

    def fit(self, data: np.ndarray) -> "IsolationForestDetector":
        """Fit Isolation Forest"""
        self.model.fit(data)
        self.is_fitted = True
        return self

    def detect(self, data: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Detect anomalies using Isolation Forest"""
        self._validate_fitted()

        predictions = self.model.predict(data)
        flags = (predictions == -1).astype(int)
        scores = -self.model.decision_function(data)

        return flags, scores


class LOFDetector(BaseAnomalyDetector):
    """Local Outlier Factor based anomaly detection"""

    def __init__(self, n_neighbors: int = 20, contamination: float = 0.01):
        """Configure LOF hyperparameters."""
        super().__init__("LOFDetector")
        self.n_neighbors = n_neighbors
        self.contamination = contamination
        self.model = LocalOutlierFactor(
            n_neighbors=n_neighbors, contamination=contamination, n_jobs=-1
        )

    def fit(self, data: np.ndarray) -> "LOFDetector":
        """Fit LOF model"""
        self.model.fit(data)
        self.is_fitted = True
        return self

    def detect(self, data: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Detect anomalies using LOF"""
        self._validate_fitted()

        predictions = self.model.fit_predict(data)
        flags = (predictions == -1).astype(int)
        scores = -self.model.negative_outlier_factor_

        return flags, scores
