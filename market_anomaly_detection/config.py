"""
Configuration management for Market Anomaly Detection Pipeline
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict


@dataclass
class DataConfig:
    """Data loading configuration"""

    csv_path: Path = Path("data/raw/msft_hourly(in).csv")
    datetime_column: str = "quote_datetime"
    price_columns: List[str] = field(default_factory=lambda: ["open", "high", "low", "close"])
    volume_columns: List[str] = field(default_factory=lambda: ["trade_volume"])
    required_columns: List[str] = field(
        default_factory=lambda: [
            "quote_datetime",
            "open",
            "high",
            "low",
            "close",
            "bid",
            "ask",
            "mid",
            "vwap",
        ]
    )
    missing_value_strategy: str = "drop"


@dataclass
class FeatureConfig:
    """Feature engineering configuration"""

    feature_columns: List[str] = field(
        default_factory=lambda: [
            "spread_pct",
            "vwap_deviation",
            "return_1h",
            "log_return",
            "high_low_range",
            "vol_6h",
            "vol_24h",
        ]
    )
    window_z: int = 30
    window_iqr: int = 30
    roll_window: int = 20


@dataclass
class AnomalyDetectionConfig:
    """Anomaly detection configuration"""

    z_threshold: int = 3
    contamination: float = 0.01
    isolation_forest_estimators: int = 200
    lof_neighbors: int = 20
    random_state: int = 42


@dataclass
class PCAConfig:
    """PCA analysis configuration"""

    n_components: int = 2
    random_state: int = 42


@dataclass
class VisualizationConfig:
    """Visualization configuration"""

    colors: Dict[str, str] = field(
        default_factory=lambda: {
            "price": "#2563eb",
            "anomaly": "#dc2626",
            "normal": "#6b7280",
        }
    )
    template: str = "plotly_white"
    figure_height: int = 600
    figure_width: int = 1200


@dataclass
class PipelineConfig:
    """Complete pipeline configuration"""

    data: DataConfig = field(default_factory=DataConfig)
    features: FeatureConfig = field(default_factory=FeatureConfig)
    anomaly_detection: AnomalyDetectionConfig = field(default_factory=AnomalyDetectionConfig)
    pca: PCAConfig = field(default_factory=PCAConfig)
    visualization: VisualizationConfig = field(default_factory=VisualizationConfig)
    output_dir: Path = Path("reports/")

    def __post_init__(self):
        """Create output directory if it doesn't exist"""
        self.output_dir.mkdir(parents=True, exist_ok=True)
