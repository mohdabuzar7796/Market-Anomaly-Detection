"""
Anomaly detection implementations
"""
import numpy as np
import pandas as pd
from typing import Tuple
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from sklearn.preprocessing import StandardScaler
from market_anomaly_detection.base.detector import BaseAnomalyDetector


class ZScoreDetector(BaseAnomalyDetector):
    """Z-score based anomaly detection"""
    
    def __init__(self, threshold: int = 3, window: int = 30):
        """Set Z-score threshold and rolling window size."""
        super().__init__("ZScoreDetector")
        self.threshold = threshold
        self.window = window
        
    def fit(self, data: np.ndarray) -> 'ZScoreDetector':
        """Z-score doesn't require fitting"""
        self.is_fitted = True
        return self
    
    def detect(self, data: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Detect anomalies using rolling Z-score"""
        self._validate_fitted()
        
        # Handle multi-variate data
        if data.ndim == 1:
            data = data.reshape(-1, 1)
        
        n_samples = data.shape[0]
        scores = np.zeros(n_samples)
        
        # Compute Z-score for each feature and take max across features
        for col_idx in range(data.shape[1]):
            series = pd.Series(data[:, col_idx])
            rolling_mean = series.rolling(window=self.window).mean()
            rolling_std = series.rolling(window=self.window).std()
            z_scores = np.abs((series - rolling_mean) / (rolling_std + 1e-8))
            scores = np.maximum(scores, z_scores.values)
        
        flags = (scores >= self.threshold).astype(int)
        
        return flags, scores


class IQRDetector(BaseAnomalyDetector):
    """IQR-based anomaly detection"""
    
    def __init__(self, window: int = 30, multiplier: float = 1.5):
        """Set rolling window size and IQR multiplier."""
        super().__init__("IQRDetector")
        self.window = window
        self.multiplier = multiplier
        
    def fit(self, data: np.ndarray) -> 'IQRDetector':
        """IQR doesn't require fitting"""
        self.is_fitted = True
        return self
    
    def detect(self, data: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Detect anomalies using rolling IQR"""
        self._validate_fitted()
        
        # Handle multi-variate data
        if data.ndim == 1:
            data = data.reshape(-1, 1)
        
        n_samples = data.shape[0]
        scores = np.zeros(n_samples)
        flags_all = np.zeros(n_samples, dtype=int)
        
        # Compute IQR for each feature
        for col_idx in range(data.shape[1]):
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
        
        return flags_all, scores


class IsolationForestDetector(BaseAnomalyDetector):
    """Isolation Forest based anomaly detection"""
    
    def __init__(self, n_estimators: int = 200, contamination: float = 0.01, random_state: int = 42):
        """Configure Isolation Forest hyperparameters."""
        super().__init__("IsolationForestDetector")
        self.n_estimators = n_estimators
        self.contamination = contamination
        self.random_state = random_state
        self.model = IsolationForest(
            n_estimators=n_estimators,
            contamination=contamination,
            random_state=random_state,
            n_jobs=-1
        )
        
    def fit(self, data: np.ndarray) -> 'IsolationForestDetector':
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
            n_neighbors=n_neighbors,
            contamination=contamination,
            n_jobs=-1
        )
        
    def fit(self, data: np.ndarray) -> 'LOFDetector':
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


class EnsembleAnomalyDetector(BaseAnomalyDetector):
    """Ensemble of multiple anomaly detectors"""
    
    def __init__(self, detectors: list = None, method: str = "voting", contamination: float = 0.01):
        """Initialize ensemble with detectors, method, and contamination."""
        super().__init__("EnsembleAnomalyDetector")
        self.detectors = detectors or []
        self.method = method
        self.contamination = contamination
        self.weights = None
        
    def add_detector(self, detector: BaseAnomalyDetector):
        """Add a detector to ensemble"""
        self.detectors.append(detector)
        
    def fit(self, data: np.ndarray) -> 'EnsembleAnomalyDetector':
        """Fit all detectors"""
        for detector in self.detectors:
            detector.fit(data)
        self.is_fitted = True
        return self
    
    def detect(self, data: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Ensemble detection with voting or weighted averaging"""
        self._validate_fitted()
        
        all_scores = []
        for detector in self.detectors:
            _, scores = detector.detect(data)
            all_scores.append(scores)
        
        all_scores = np.array(all_scores)
        
        if self.method == "voting":
            # Average the normalized scores
            normalized = (all_scores - all_scores.min(axis=1, keepdims=True)) / \
                        (all_scores.max(axis=1, keepdims=True) - all_scores.min(axis=1, keepdims=True) + 1e-8)
            ensemble_scores = normalized.mean(axis=0)
        elif self.method == "weighted":
            if self.weights is None:
                # Calculate weights based on variance
                self.weights = all_scores.std(axis=1)
                self.weights = self.weights / self.weights.sum()
            ensemble_scores = np.dot(self.weights, all_scores)
        else:
            raise ValueError(f"Unknown ensemble method: {self.method}")
        
        # Generate flags based on score distribution
        threshold = np.quantile(ensemble_scores, 1 - self.contamination)
        flags = (ensemble_scores >= threshold).astype(int)
        
        return flags, ensemble_scores
