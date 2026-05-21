# Quick Start Guide

## Installation

1. **Setup virtual environment**
```bash
python -m venv .venv
.venv\Scripts\activate
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Verify structure**
```
Market-Anomaly-Detection/
├── src/
│   ├── config.py
│   ├── base/
│   ├── data/
│   ├── detectors/
│   ├── analysis/
│   ├── visualization/
│   └── pipelines/
├── data/
│   └── msft_hourly(in).csv
├── reports/
├── main.py
├── examples.py
└── README_PIPELINE.md
```

## Quick Start (3 lines of code)

```python
from market_anomaly_detection.pipelines.market_anomaly_pipeline import MarketAnomalyDetectionPipeline

pipeline = MarketAnomalyDetectionPipeline()
results = pipeline.run()
```

## Common Tasks

### 1. Run Full Pipeline
```python
from market_anomaly_detection.pipelines.market_anomaly_pipeline import MarketAnomalyDetectionPipeline

pipeline = MarketAnomalyDetectionPipeline()
results = pipeline.run()
df_results = pipeline.get_results()
pipeline.export_results()
```

### 2. Customize Anomaly Detection Threshold
```python
from market_anomaly_detection.config import PipelineConfig, AnomalyDetectionConfig

config = PipelineConfig(
    anomaly_detection=AnomalyDetectionConfig(
        z_threshold=2.5,  # Stricter
        contamination=0.05  # Allow 5% anomalies
    )
)

pipeline = MarketAnomalyDetectionPipeline(config)
pipeline.run()
```

### 3. Use Only Specific Detectors
```python
from market_anomaly_detection.detectors.ensemble import ZScoreDetector, IsolationForestDetector
from market_anomaly_detection.data.processor import DataLoader
import numpy as np

loader = DataLoader("data/msft_hourly(in).csv")
df = loader.load()

# Run specific detectors
z_detector = ZScoreDetector(threshold=3, window=30)
if_detector = IsolationForestDetector()

data = df[['close']].values
z_flags, z_scores = z_detector.fit_detect(data)
if_flags, if_scores = if_detector.fit_detect(data)

print(f"Z-Score anomalies: {z_flags.sum()}")
print(f"IF anomalies: {if_flags.sum()}")
```

### 4. Analyze Feature Importance
```python
from market_anomaly_detection.analysis.pca_analyzer import PCAAnalyzer

pca = PCAAnalyzer(n_components=3)
results = pca.analyze(df, ['spread_pct', 'log_return', 'vol_24h'])

print("Explained Variance:", results['explained_variance'])
print("Dominant Variables:", results['dominant_variables'])
```

### 5. Get Correlation Analysis
```python
from market_anomaly_detection.analysis.pca_analyzer import CorrelationAnalyzer

corr = CorrelationAnalyzer(method='spearman')
results = corr.analyze(df, ['open', 'high', 'low', 'close', 'volume'])

print("Highly correlated pairs:")
for pair in results['high_correlation_pairs']:
    print(f"  {pair['feature1']} <-> {pair['feature2']}: {pair['correlation']:.3f}")
```

### 6. Compare Multiple Detectors
```python
from market_anomaly_detection.detectors.ensemble import *
from market_anomaly_detection.data.processor import DataLoader

loader = DataLoader("data/msft_hourly(in).csv")
df = loader.load()
data = df[['close']].values

detectors = [
    ZScoreDetector(threshold=3),
    IQRDetector(multiplier=1.5),
    IsolationForestDetector(),
    LOFDetector()
]

results = {}
for detector in detectors:
    flags, scores = detector.fit_detect(data)
    results[detector.name] = {
        'anomalies': flags.sum(),
        'mean_score': scores.mean()
    }

for name, metrics in results.items():
    print(f"{name}: {metrics['anomalies']} anomalies")
```

### 7. Export Results with Custom Path
```python
from market_anomaly_detection.config import PipelineConfig
from pathlib import Path

config = PipelineConfig(output_dir=Path("my_reports/"))
pipeline = MarketAnomalyDetectionPipeline(config)
pipeline.run()
pipeline.export_results("my_reports/custom_results.csv")
```

### 8. Integrate with Existing Data
```python
import pandas as pd
from market_anomaly_detection.pipelines.market_anomaly_pipeline import MarketAnomalyDetectionPipeline

# Load your own data
df = pd.read_csv("your_data.csv")

# Run pipeline on your data
pipeline = MarketAnomalyDetectionPipeline()
pipeline.df_raw = df
results = pipeline.run()
```

## Configuration Examples

### Conservative Detection (Lower False Positives)
```python
from market_anomaly_detection.config import PipelineConfig, AnomalyDetectionConfig

config = PipelineConfig(
    anomaly_detection=AnomalyDetectionConfig(
        z_threshold=4,  # Higher threshold
        contamination=0.001,  # Only 0.1% flagged
        isolation_forest_estimators=500  # More trees
    )
)
```

### Aggressive Detection (Lower False Negatives)
```python
config = PipelineConfig(
    anomaly_detection=AnomalyDetectionConfig(
        z_threshold=2,  # Lower threshold
        contamination=0.05,  # 5% flagged
        isolation_forest_estimators=100  # Fewer trees
    )
)
```

### Focus on Volatility Anomalies
```python
from market_anomaly_detection.config import FeatureConfig

config = PipelineConfig(
    features=FeatureConfig(
        feature_columns=["vol_6h", "vol_24h", "log_return"],
        window_z=14,  # Shorter window
        window_iqr=14
    )
)
```

## Troubleshooting

### Issue: "Data not loaded" error
```python
# Always load data first
loader = DataLoader(csv_path)
df = loader.load()

# OR pass to pipeline
pipeline = MarketAnomalyDetectionPipeline()
results = pipeline.run(data=df)
```

### Issue: Missing columns
```python
# Check available columns
print(df.columns)

# Update feature config
config = PipelineConfig(
    features=FeatureConfig(
        feature_columns=[col for col in df.columns if col in ['spread_pct', 'log_return']]
    )
)
```

### Issue: Memory error with large dataset
```python
# Sample data
df_sample = df.iloc[::10]  # Every 10th row

# Or reduce PCA components
config = PipelineConfig(pca=PCAConfig(n_components=1))
```

## Performance Tips

1. **Reduce window sizes** for faster processing
2. **Decrease PCA components** to 1-2 for speed
3. **Use fewer detector methods** if not needed
4. **Sample data** if working with large datasets
5. **Parallelize** detector fitting with `n_jobs=-1`

## Next Steps

1. Check `examples.py` for advanced usage
2. Read `README_PIPELINE.md` for architecture details
3. Explore `src/` modules for specific implementations
4. Customize detectors and add new analysis methods
5. Deploy pipeline as REST API or scheduled task

## Support

For issues or questions:
1. Check existing code in `src/` modules
2. Review examples in `examples.py`
3. Test individual components independently
4. Add logging/debug prints to trace execution

## Testing Your Setup

```python
# test_setup.py
from market_anomaly_detection.pipelines.market_anomaly_pipeline import MarketAnomalyDetectionPipeline
from market_anomaly_detection.config import PipelineConfig

# Test basic pipeline
config = PipelineConfig()
pipeline = MarketAnomalyDetectionPipeline(config)

# Test on small sample (first 100 records)
import pandas as pd
df = pd.read_csv("data/msft_hourly(in).csv")
results = pipeline.run(data=df.iloc[:100])

print("✓ Pipeline works!")
print(f"✓ Detected {results['anomaly_stats']['anomaly_count']} anomalies")
```

Run with:
```bash
python test_setup.py
```
