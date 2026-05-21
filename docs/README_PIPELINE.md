# Market Anomaly Detection Pipeline - OOP Architecture

## Overview

This is an industry-level, production-ready pipeline for detecting market anomalies in financial time-series data (MSFT hourly OHLCV data). The architecture follows **SOLID principles** and uses **OOP design patterns** for modularity, scalability, and maintainability.

## Architecture

```
src/
├── config.py                          # Configuration management (dataclasses)
├── base/
│   └── detector.py                   # Abstract base classes
├── data/
│   └── processor.py                  # Data loading & processing
├── detectors/
│   └── ensemble.py                   # Anomaly detection methods
├── analysis/
│   └── pca_analyzer.py              # PCA & correlation analysis
├── visualization/
│   └── plotter.py                   # Plotly visualizations
└── pipelines/
    └── market_anomaly_pipeline.py   # Main orchestration pipeline
```

## Key Components

### 1. **Configuration Management** (`config.py`)
- Uses Python dataclasses for type-safe configuration
- Modular sub-configs: `DataConfig`, `FeatureConfig`, `AnomalyDetectionConfig`, etc.
- Easy to extend and customize

```python
config = PipelineConfig(
    data=DataConfig(csv_path="data.csv"),
    anomaly_detection=AnomalyDetectionConfig(z_threshold=3)
)
```

### 2. **Base Classes** (`base/detector.py`)
- **`BaseAnomalyDetector`**: Abstract interface for all detectors
- **`BasePipeline`**: Abstract interface for pipelines
- **`BaseFeatureCalculator`**: Abstract interface for feature engineering
- **`BaseAnalyzer`**: Abstract interface for analysis

All concrete implementations inherit from these base classes, ensuring consistency and modularity.

### 3. **Data Processing** (`data/processor.py`)
- **`DataLoader`**: Load CSV data with validation
- **`DataProcessor`**: Data quality checks (price consistency, duplicates)
- **`FinancialMetricsCalculator`**: Calculate returns, volatility, spreads

Each class has single responsibility and is independently testable.

### 4. **Anomaly Detection** (`detectors/ensemble.py`)
Implements 4 distinct detection methods:

- **`ZScoreDetector`**: Rolling Z-score with configurable threshold
- **`IQRDetector`**: Interquartile Range method
- **`IsolationForestDetector`**: Ensemble tree-based isolation
- **`LOFDetector`**: Local Outlier Factor (density-based)
- **`EnsembleAnomalyDetector`**: Combines all methods via voting or weighted averaging

**Factory-like pattern**: Easy to swap, add, or remove detectors.

### 5. **Analysis** (`analysis/pca_analyzer.py`)
- **`PCAAnalyzer`**: Dimensionality reduction with loadings & variance explained
- **`CorrelationAnalyzer`**: Spearman/Pearson correlations
- **`AnomalyStatisticsAnalyzer`**: Summary statistics

### 6. **Visualization** (`visualization/plotter.py`)
- **`AnomalyVisualizer`**: Multiple interactive Plotly charts
  - Price with anomalies overlay
  - PCA scatter with anomaly clusters
  - Score distribution with threshold
  - Correlation heatmap
  - Multi-detector comparison

### 7. **Main Pipeline** (`pipelines/market_anomaly_pipeline.py`)
**`MarketAnomalyDetectionPipeline`**: Orchestrates entire workflow
- 10 sequential steps with logging
- Manages data flow between components
- Collects and organizes results
- Exports to CSV and HTML

## Design Patterns Used

| Pattern | Component | Benefit |
|---------|-----------|---------|
| **Strategy** | Detectors | Swap detection algorithms at runtime |
| **Template Method** | Base classes | Define algorithm structure in base, implement in subclasses |
| **Factory** | Pipeline initialization | Create detector instances programmatically |
| **Composition** | Pipeline | Flexible component assembly |
| **Dependency Injection** | All classes | Loose coupling via constructor injection |

## SOLID Principles

1. **Single Responsibility**: Each class has one reason to change
   - `DataLoader` only loads data
   - `ZScoreDetector` only does Z-score detection
   
2. **Open/Closed**: Open for extension, closed for modification
   - Add new detectors by inheriting `BaseAnomalyDetector`
   - No changes to existing code needed

3. **Liskov Substitution**: All detector subclasses work interchangeably
   ```python
   for detector in detectors:  # Works with any BaseAnomalyDetector
       flags, scores = detector.fit_detect(data)
   ```

4. **Interface Segregation**: Small, focused interfaces
   - `BaseAnomalyDetector` vs `BaseAnalyzer` vs `BaseFeatureCalculator`
   - Classes implement only what they need

5. **Dependency Inversion**: Depend on abstractions, not concretions
   - Pipeline depends on `BasePipeline`, `BaseAnomalyDetector`, etc.
   - Not on concrete implementations

## Usage

### Basic Usage
```python
from market_anomaly_detection.pipelines.market_anomaly_pipeline import MarketAnomalyDetectionPipeline

pipeline = MarketAnomalyDetectionPipeline()
results = pipeline.run()
df_results = pipeline.get_results()
```

### Custom Configuration
```python
from market_anomaly_detection.config import PipelineConfig, AnomalyDetectionConfig

config = PipelineConfig(
    anomaly_detection=AnomalyDetectionConfig(
        z_threshold=3,
        contamination=0.02,
        isolation_forest_estimators=300
    )
)

pipeline = MarketAnomalyDetectionPipeline(config)
results = pipeline.run()
```

### Individual Components
```python
from market_anomaly_detection.data.processor import DataLoader, FinancialMetricsCalculator
from market_anomaly_detection.detectors.ensemble import ZScoreDetector

loader = DataLoader("data.csv")
df = loader.load()

calc = FinancialMetricsCalculator()
df_featured = calc.calculate(df)

detector = ZScoreDetector(threshold=3, window=30)
flags, scores = detector.fit_detect(df_featured[['close']].values)
```

## Output

Pipeline generates:
1. **CSV Export**: `reports/anomaly_detection_results.csv`
   - Original data + all detector flags/scores
   - PCA components
   - Final ensemble anomaly flag & score

2. **Visualizations**: HTML files in `reports/`
   - `price_with_anomalies.html`
   - `pca_scatter.html`
   - `score_distribution.html`
   - `correlation_heatmap.html`

3. **Results Dictionary**: Complete results object
   ```python
   results = {
       'detector_results': {...},
       'pca': {...},
       'correlation': {...},
       'anomaly_stats': {...},
       'visualizations': {...}
   }
   ```

## Extension Points

### Add a New Detector
```python
from market_anomaly_detection.base.detector import BaseAnomalyDetector

class MyCustomDetector(BaseAnomalyDetector):
    def fit(self, data):
        # Implementation
        self.is_fitted = True
        return self
    
    def detect(self, data):
        # Return (flags, scores)
        return flags, scores
```

### Add a New Analysis
```python
from market_anomaly_detection.base.detector import BaseAnalyzer

class MyAnalyzer(BaseAnalyzer):
    def analyze(self, data):
        # Perform analysis
        self.analysis_results = {...}
        return self.analysis_results
```

### Custom Pipeline
```python
from market_anomaly_detection.base.detector import BasePipeline

class MyPipeline(BasePipeline):
    def run(self, data):
        # Implement pipeline logic
        return self.results
```

## Configuration Reference

```python
PipelineConfig(
    data=DataConfig(
        csv_path=Path("data/msft_hourly(in).csv"),
        datetime_column="quote_datetime",
        price_columns=["open", "high", "low", "close"]
    ),
    features=FeatureConfig(
        feature_columns=["spread_pct", "log_return", "vol_24h"],
        window_z=30,
        window_iqr=30
    ),
    anomaly_detection=AnomalyDetectionConfig(
        z_threshold=3,
        contamination=0.01,
        isolation_forest_estimators=200,
        lof_neighbors=20
    ),
    pca=PCAConfig(n_components=2),
    visualization=VisualizationConfig(
        colors={"price": "#2563eb", "anomaly": "#dc2626"},
        template="plotly_white"
    ),
    output_dir=Path("reports/")
)
```

## Testing

Each component can be tested independently:
```python
# Test detector
detector = ZScoreDetector(threshold=3)
test_data = np.random.randn(100, 1)
flags, scores = detector.fit_detect(test_data)
assert flags.shape == (100,)

# Test processor
processor = DataProcessor()
test_df = pd.DataFrame({'bid': [1, 2], 'ask': [2, 1]})
issues = processor.validate_price_data(test_df, ['bid', 'ask'])
assert 'bid_gt_ask' in issues
```

## Performance Considerations

- **Scalability**: Pipeline handles large datasets efficiently
  - StandardScaler from sklearn
  - Vectorized numpy operations
  - Optional parallel processing (`n_jobs=-1`)

- **Memory**: Efficient data structures
  - Pandas DataFrames with proper dtypes
  - Lazy evaluation where possible

- **Speed**: Configurable precision vs performance
  - Adjust window sizes for speed
  - Control number of PCA components
  - Tune detector parameters

## Future Enhancements

1. **Multi-timeframe analysis** (1h, 4h, 1d data simultaneously)
2. **Deep learning detectors** (LSTM, Autoencoder)
3. **Backtesting module** for strategy validation
4. **Database integration** for data persistence
5. **REST API** for model serving
6. **Real-time streaming** support (Kafka, WebSocket)
7. **Model persistence** (joblib, pickle)
8. **Hyperparameter tuning** (Optuna, Hyperopt)

## Dependencies

See `requirements.txt`:
- pandas, numpy
- scikit-learn
- plotly
- python-dateutil

## License

MIT License

## Author

Market Anomaly Detection Team
