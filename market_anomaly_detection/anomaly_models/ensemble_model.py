"""
Ensemble anomaly detection models
"""

import numpy as np
from typing import Tuple
from market_anomaly_detection.base.interfaces import BaseAnomalyDetector


class EnsembleAnomalyDetector(BaseAnomalyDetector):
    """Ensemble of multiple anomaly detectors"""

    def __init__(
        self,
        detectors: list = None,
        method: str = "voting",
        contamination: float = 0.01,
    ):
        """Initialize ensemble with detectors, method, and contamination."""
        super().__init__("EnsembleAnomalyDetector")
        self.detectors = detectors or []
        self.method = method
        self.contamination = contamination
        self.weights = None

    def add_detector(self, detector: BaseAnomalyDetector):
        """Add a detector to ensemble"""
        self.detectors.append(detector)

    def fit(self, data: np.ndarray) -> "EnsembleAnomalyDetector":
        """Fit all detectors"""
        for detector in self.detectors:
            detector.fit(data)
        self.is_fitted = True
        return self

    def detect(self, data: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Ensemble detection with voting, weighted averaging, or combined logic"""
        self._validate_fitted()

        all_scores = []
        all_flags = []
        for detector in self.detectors:
            flags, scores = detector.detect(data)
            all_scores.append(scores)
            all_flags.append(flags)

        all_scores = np.array(all_scores)
        all_flags = np.array(all_flags)

        if self.method == "voting":
            # Average the normalized scores
            normalized = (all_scores - all_scores.min(axis=1, keepdims=True)) / (
                all_scores.max(axis=1, keepdims=True) - all_scores.min(axis=1, keepdims=True) + 1e-8
            )
            ensemble_scores = normalized.mean(axis=0)
            threshold = np.quantile(ensemble_scores, 1 - self.contamination)
            flags = (ensemble_scores >= threshold).astype(int)
        elif self.method == "weighted":
            if self.weights is None:
                # Calculate weights based on variance
                self.weights = all_scores.std(axis=1)
                self.weights = self.weights / (self.weights.sum() + 1e-8)
            ensemble_scores = np.dot(self.weights, all_scores)
            threshold = np.quantile(ensemble_scores, 1 - self.contamination)
            flags = (ensemble_scores >= threshold).astype(int)
        elif self.method == "combined":
            # Replicate notebook's exact combined logic
            z_idx, iqr_idx, if_idx, lof_idx = -1, -1, -1, -1
            for i, d in enumerate(self.detectors):
                if d.name == "ZScoreDetector":
                    z_idx = i
                elif d.name == "IQRDetector":
                    iqr_idx = i
                elif d.name == "IsolationForestDetector":
                    if_idx = i
                elif d.name == "LOFDetector":
                    lof_idx = i

            if if_idx >= 0 and lof_idx >= 0:

                def safe_minmax(s):
                    den = s.max() - s.min()
                    return (s - s.min()) / den if den > 0 else np.zeros_like(s)

                if_norm = safe_minmax(all_scores[if_idx])
                lof_norm = safe_minmax(all_scores[lof_idx])
                ensemble_scores = (if_norm + lof_norm) / 2.0
                ens_thr = np.quantile(ensemble_scores, 1 - self.contamination)

                ensemble_flag = ((all_flags[if_idx] == 1) & (all_flags[lof_idx] == 1)) | (
                    ensemble_scores >= ens_thr
                )
                ensemble_flag = ensemble_flag.astype(int)
            else:
                ensemble_scores = np.zeros(data.shape[0])
                ensemble_flag = np.zeros(data.shape[0], dtype=int)

            self.ml_ensemble_flags_ = ensemble_flag

            flags = ensemble_flag
            if iqr_idx >= 0:
                flags = flags & (all_flags[iqr_idx] == 1)
            if z_idx >= 0:
                flags = flags & (all_flags[z_idx] == 1)
        else:
            raise ValueError(f"Unknown ensemble method: {self.method}")

        return flags.astype(int), ensemble_scores
