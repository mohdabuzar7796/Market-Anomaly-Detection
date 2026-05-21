# OOP Pipeline - Complete Documentation Index

## 📚 Documentation Files

### 1. **README_PIPELINE.md** - Architecture & Design
- Complete system overview
- Design patterns (Strategy, Factory, Template Method, etc.)
- SOLID principles application
- Extension points for customization
- Configuration reference
- Dependency information

**Start here if**: You want to understand the architecture and design decisions.

### 2. **ARCHITECTURE.md** - Detailed Technical Design
- ASCII diagrams of system architecture
- Class hierarchies and relationships
- Data flow visualization
- Component interaction diagrams
- Detector comparison matrix
- Execution flow step-by-step
- Module dependencies
- Design rationale

**Start here if**: You need visual understanding or are extending the system.

### 3. **QUICKSTART.md** - Getting Started
- Installation instructions
- 3-line code example
- 8 common tasks with code
- Configuration examples (conservative, aggressive, etc.)
- Troubleshooting guide
- Performance tips
- Testing your setup

**Start here if**: You want to run the pipeline immediately.

### 4. **requirements-pipeline.txt** - Dependencies
All required Python packages with version pins.

**Use this for**: Installation and dependency management.

## 🏗️ Project Structure

```
src/
├── config.py                      # Configuration management
│                                  # PipelineConfig, DataConfig, etc.
│
├── base/
│   └── detector.py               # Abstract base classes
│                                  # BaseAnomalyDetector
│                                  # BasePipeline
│                                  # BaseFeatureCalculator
│                                  # BaseAnalyzer
│
├── data/
│   └── processor.py              # Data handling
│                                  # DataLoader
│                                  # DataProcessor
│                                  # FinancialMetricsCalculator
│
├── detectors/
│   └── ensemble.py               # Anomaly detection algorithms
│                                  # ZScoreDetector
│                                  # IQRDetector
│                                  # IsolationForestDetector
│                                  # LOFDetector
│                                  # EnsembleAnomalyDetector
│
├── analysis/
│   └── pca_analyzer.py           # Analysis tools
│                                  # PCAAnalyzer
│                                  # CorrelationAnalyzer
│                                  # AnomalyStatisticsAnalyzer
│
├── visualization/
│   └── plotter.py                # Visualization module
│                                  # AnomalyVisualizer
│
└── pipelines/
    └── market_anomaly_pipeline.py # Main orchestration
                                    # MarketAnomalyDetectionPipeline
                                    # run_pipeline() helper
```

## 📖 Module Descriptions

### `config.py` - Configuration Management
- **Purpose**: Centralized, type-safe configuration
- **Classes**: 
  - `DataConfig`: Data loading parameters
  - `FeatureConfig`: Feature engineering settings
  - `AnomalyDetectionConfig`: Detector parameters
  - `PCAConfig`: Dimensionality reduction settings
  - `VisualizationConfig`: Chart styling
  - `PipelineConfig`: Complete configuration
- **Why OOP**: Easy to modify, validate, and pass around

### `base/detector.py` - Base Classes
- **Purpose**: Abstract interfaces ensuring consistency
- **Classes**:
  - `BaseAnomalyDetector`: All detectors must implement
  - `BasePipeline`: All pipelines must implement
  - `BaseFeatureCalculator`: All feature engineers must implement
  - `BaseAnalyzer`: All analyzers must implement
- **Why OOP**: Polymorphism, extensibility, clear contracts

### `data/processor.py` - Data Operations
- **Purpose**: Handle data loading, validation, and feature engineering
- **Classes**:
  - `DataLoader`: Load CSV with error handling
  - `DataProcessor`: Quality checks (OHLC, duplicates, etc.)
  - `FinancialMetricsCalculator`: Calculate returns, volatility, spreads
- **Why OOP**: Single responsibility, reusable in isolation

### `detectors/ensemble.py` - Anomaly Detection
- **Purpose**: Implement 4+ anomaly detection methods
- **Classes**:
  - `ZScoreDetector`: Rolling Z-score method
  - `IQRDetector`: Interquartile range method
  - `IsolationForestDetector`: Tree-based isolation
  - `LOFDetector`: Density-based detection
  - `EnsembleAnomalyDetector`: Voting/weighted combination
- **Why OOP**: Strategy pattern for swappable algorithms

### `analysis/pca_analyzer.py` - Analysis Tools
- **Purpose**: Dimension reduction and statistics
- **Classes**:
  - `PCAAnalyzer`: Principal component analysis
  - `CorrelationAnalyzer`: Feature correlation matrix
  - `AnomalyStatisticsAnalyzer`: Summary statistics
- **Why OOP**: Independent analysis tools, reusable

### `visualization/plotter.py` - Visualization
- **Purpose**: Generate interactive Plotly charts
- **Classes**:
  - `AnomalyVisualizer`: Price overlay, PCA scatter, distributions, heatmaps
- **Why OOP**: Encapsulate styling and chart logic

### `pipelines/market_anomaly_pipeline.py` - Main Pipeline
- **Purpose**: Orchestrate all components in workflow
- **Classes**:
  - `MarketAnomalyDetectionPipeline`: Main orchestrator
- **Functions**:
  - `run_pipeline()`: Helper function to quickly run
- **Why OOP**: Centralized workflow, easy to extend

## 🎯 Key OOP Principles Applied

### Single Responsibility
- Each class has ONE reason to change
- `DataLoader` only loads data
- `ZScoreDetector` only does Z-score detection

### Open/Closed
- Open for extension (add new detectors)
- Closed for modification (don't change existing code)
- Example: Add detector without modifying pipeline

### Liskov Substitution
- All detectors are interchangeable
- Pipeline doesn't care which detector is used
- Easy to swap implementations

### Interface Segregation
- Small focused interfaces
- Classes implement only what they need
- `BaseAnomalyDetector` vs `BaseAnalyzer` vs `BaseFeatureCalculator`

### Dependency Inversion
- Pipeline depends on abstractions (base classes)
- Not on concrete implementations
- Loose coupling, easy testing

## 🔄 Workflow Example

```python
# 1. Initialize with configuration
config = PipelineConfig(
    anomaly_detection=AnomalyDetectionConfig(
        z_threshold=3,
        contamination=0.01
    )
)

# 2. Create pipeline (dependency injection)
pipeline = MarketAnomalyDetectionPipeline(config)

# 3. Run (orchestrates all steps)
results = pipeline.run()

# 4. Results include:
# - detector_results: Individual detector outputs
# - pca: PCA analysis with loadings
# - correlation: Feature correlations
# - anomaly_stats: Summary statistics
# - visualizations: Interactive HTML charts
```

## 🧪 Testing Strategy

Each component can be tested independently:

```python
# Test detector in isolation
detector = ZScoreDetector(threshold=3)
test_data = np.random.randn(100, 1)
flags, scores = detector.fit_detect(test_data)

# Test processor in isolation
processor = DataProcessor()
test_df = pd.DataFrame({'bid': [1, 2], 'ask': [2, 1]})
issues = processor.validate_price_data(test_df, ['bid', 'ask'])

# Test analyzer in isolation
analyzer = PCAAnalyzer(n_components=2)
results = analyzer.analyze(df, feature_cols)
```

## 🚀 Extension Examples

### Add New Detector
```python
from market_anomaly_detection.base.detector import BaseAnomalyDetector

class MyCustomDetector(BaseAnomalyDetector):
    def fit(self, data):
        # Your fitting logic
        self.is_fitted = True
        return self
    
    def detect(self, data):
        # Your detection logic
        return flags, scores  # (N,) arrays

# Use immediately
detector = MyCustomDetector("MyDetector")
flags, scores = detector.fit_detect(data)
```

### Create New Pipeline
```python
from market_anomaly_detection.base.detector import BasePipeline

class MyPipeline(BasePipeline):
    def run(self, data):
        # Custom workflow
        self.results['custom_key'] = custom_output
        return self.results
```

## 📊 Performance Characteristics

| Component | Speed | Memory | Scalability |
|-----------|-------|--------|-------------|
| DataLoader | O(n) | O(n) | Good |
| ZScoreDetector | O(n) | O(n) | Excellent |
| IQRDetector | O(n) | O(n) | Excellent |
| IsolationForest | O(n*log n) | O(n) | Good |
| LOFDetector | O(n²) | O(n) | Fair |
| Ensemble | O(n) | O(n) | Good |
| PCA | O(n*m²) | O(n*m) | Fair |

## 🔍 Debugging Tips

1. **Check configuration**
   ```python
   print(config.anomaly_detection)
   ```

2. **Run individual components**
   ```python
   detector = ZScoreDetector()
   flags, scores = detector.fit_detect(data)
   ```

3. **Inspect intermediate results**
   ```python
   pipeline = MarketAnomalyDetectionPipeline(config)
   pipeline.run()
   print(pipeline.df_processed.shape)
   print(pipeline.df_featured.columns)
   ```

4. **Enable logging**
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

## 📝 Common Customizations

### 1. Different Feature Set
```python
config = PipelineConfig(
    features=FeatureConfig(
        feature_columns=['vol_6h', 'vol_24h', 'log_return']
    )
)
```

### 2. Custom Threshold
```python
config = PipelineConfig(
    anomaly_detection=AnomalyDetectionConfig(
        z_threshold=2.5,  # More sensitive
        contamination=0.02  # Allow more anomalies
    )
)
```

### 3. Different Detectors
```python
# In pipeline.__init__, modify _initialize_detectors()
def _initialize_detectors(self):
    return [
        ZScoreDetector(),
        IsolationForestDetector(),
        # Skip IQRDetector and LOFDetector if not needed
    ]
```

### 4. Custom Visualization
```python
from market_anomaly_detection.visualization.plotter import AnomalyVisualizer

viz = AnomalyVisualizer(config.visualization)
fig = viz.plot_price_with_anomalies(df)
fig.show()

# or customize further
fig.update_layout(title="My Custom Title")
```

## 🎓 Learning Path

1. **Start**: Read QUICKSTART.md, run pipeline
2. **Understand**: Read README_PIPELINE.md for architecture
3. **Visualize**: Read ARCHITECTURE.md for diagrams
4. **Extend**: Add custom detectors following examples
5. **Integrate**: Use pipeline in your application

## 🔗 File Relationships

```
main.py
  └── imports MarketAnomalyDetectionPipeline
      ├── uses PipelineConfig
      ├── uses DataLoader, DataProcessor
      ├── uses ZScoreDetector, IQRDetector, etc.
      ├── uses PCAAnalyzer, CorrelationAnalyzer
      └── uses AnomalyVisualizer

examples.py
  └── demonstrates all usage patterns

tests/ (future)
  ├── test_detectors.py
  ├── test_processors.py
  └── test_pipeline.py
```

## 💡 Pro Tips

1. **Use configuration for different scenarios**
   - Create separate PipelineConfig for production, testing, etc.

2. **Leverage dependency injection**
   - Pass different detectors to ensemble for A/B testing

3. **Compose detectors strategically**
   - Combine fast detectors (Z-score, IQR) with slow ones (LOF, IF)

4. **Cache PCA results**
   - Reuse PCA analyzer across multiple datasets

5. **Monitor detector disagreement**
   - When detectors disagree, investigate those points

## 📞 Support & Contribution

For issues, enhancements, or questions:
1. Check existing documentation
2. Review code comments
3. Test components independently
4. Follow SOLID principles when extending

---

**Generated**: May 2026  
**Version**: 1.0.0  
**Status**: Production Ready
