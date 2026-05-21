"""
Market Anomaly Detection Pipeline Package
Industry-level OOP implementation with modular architecture
"""

__version__ = "1.0.0"
__author__ = "Market Anomaly Detection Team"

from market_anomaly_detection.config import PipelineConfig
from market_anomaly_detection.pipelines.market_anomaly_pipeline import MarketAnomalyDetectionPipeline

__all__ = [
    'PipelineConfig',
    'MarketAnomalyDetectionPipeline'
]
