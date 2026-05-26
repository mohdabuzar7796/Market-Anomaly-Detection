import numpy as np

from market_anomaly_detection.base.detector import BaseAnomalyDetector
from market_anomaly_detection.detectors.ensemble import EnsembleAnomalyDetector


class DummyDetector(BaseAnomalyDetector):
    """Minimal detector for testing ensemble behavior."""

    def __init__(self, scores: np.ndarray):
        """Store the scores returned during detection."""
        super().__init__("DummyDetector")
        self._scores = scores

    def fit(self, data: np.ndarray) -> "DummyDetector":
        """Mark the detector as fitted for tests."""
        self.is_fitted = True
        return self

    def detect(self, data: np.ndarray):
        """Return stored scores with simple flags."""
        self._validate_fitted()
        flags = (self._scores > 0).astype(int)
        return flags, self._scores


def test_ensemble_contamination_configures_threshold():
    """Ensure ensemble uses contamination to compute thresholds."""
    scores = np.array([0.0, 0.0, 0.0, 1.0])
    detectors = [DummyDetector(scores), DummyDetector(scores)]
    ensemble = EnsembleAnomalyDetector(detectors, method="voting", contamination=0.25)

    data = np.zeros((4, 1))
    ensemble.fit(data)
    flags, ensemble_scores = ensemble.detect(data)

    threshold = np.quantile(ensemble_scores, 1 - 0.25)
    expected_flags = (ensemble_scores >= threshold).astype(int)

    assert np.array_equal(flags, expected_flags)
