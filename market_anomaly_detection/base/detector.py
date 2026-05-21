"""
Base classes for anomaly detection
"""
from abc import ABC, abstractmethod
import pandas as pd
import numpy as np
from typing import Dict, Tuple, Any


class BaseAnomalyDetector(ABC):
    """Abstract base class for anomaly detectors"""
    
    def __init__(self, name: str):
        self.name = name
        self.is_fitted = False
        self.model = None
        
    @abstractmethod
    def fit(self, data: np.ndarray) -> 'BaseAnomalyDetector':
        """Fit the detector on data"""
        pass
    
    @abstractmethod
    def detect(self, data: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Detect anomalies
        Returns: (anomaly_flags, anomaly_scores)
        """
        pass
    
    def fit_detect(self, data: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Fit and detect in one step"""
        self.fit(data)
        return self.detect(data)
    
    def _validate_fitted(self):
        """Check if model is fitted"""
        if not self.is_fitted:
            raise ValueError(f"{self.name} model must be fitted before detection")


class BasePipeline(ABC):
    """Abstract base class for pipelines"""
    
    def __init__(self, name: str):
        self.name = name
        self.results = {}
        
    @abstractmethod
    def run(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Execute the pipeline"""
        pass
    
    def save_results(self, output_path: str):
        """Save pipeline results"""
        # Implementation in concrete classes
        pass


class BaseFeatureCalculator(ABC):
    """Abstract base class for feature calculation"""
    
    def __init__(self, name: str):
        self.name = name
        
    @abstractmethod
    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate features"""
        pass


class BaseAnalyzer(ABC):
    """Abstract base class for analysis"""
    
    def __init__(self, name: str):
        self.name = name
        self.analysis_results = {}
        
    @abstractmethod
    def analyze(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Perform analysis"""
        pass
