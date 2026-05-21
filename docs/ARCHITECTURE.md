# Architecture Overview & Class Diagrams

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    MARKET ANOMALY DETECTION PIPELINE                │
└─────────────────────────────────────────────────────────────────────┘

                              Pipeline Orchestrator
                         (MarketAnomalyDetectionPipeline)
                                    │
                 ┌──────────────────┼──────────────────┐
                 │                  │                  │
            ┌────▼────┐      ┌──────▼────────┐  ┌─────▼─────┐
            │   DATA  │      │  DETECTORS    │  │ ANALYSIS  │
            │ LAYER   │      │   LAYER       │  │ LAYER     │
            └────┬────┘      └──────┬────────┘  └─────┬─────┘
                 │                  │                  │
        ┌────────▼────────┐  ┌──────▼────────────┐    │
        │ • DataLoader    │  │ • ZScoreDetector │    │
        │ • DataProcessor │  │ • IQRDetector    │    │
        │ • FeatCalc      │  │ • IsolationForest│    │
        └────────┬────────┘  │ • LOFDetector    │    │
                 │           │ • Ensemble       │    │
                 │           └──────┬───────────┘    │
                 └───────────────────┼────────────────┘
                                     │
                         ┌───────────▼────────────┐
                         │   VISUALIZATION       │
                         │   (AnomalyVisualizer) │
                         └───────────┬────────────┘
                                     │
                         ┌───────────▼────────────┐
                         │   RESULTS             │
                         │ • CSV Export          │
                         │ • HTML Charts         │
                         │ • Statistics          │
                         └───────────────────────┘
```

## Class Hierarchy

```
BaseAnomalyDetector (Abstract)
├── ZScoreDetector
├── IQRDetector
├── IsolationForestDetector
├── LOFDetector
└── EnsembleAnomalyDetector

BaseFeatureCalculator (Abstract)
├── DataProcessor
└── FinancialMetricsCalculator

BaseAnalyzer (Abstract)
├── PCAAnalyzer
├── CorrelationAnalyzer
└── AnomalyStatisticsAnalyzer

BasePipeline (Abstract)
└── MarketAnomalyDetectionPipeline

PipelineConfig (Dataclass)
├── DataConfig
├── FeatureConfig
├── AnomalyDetectionConfig
├── PCAConfig
└── VisualizationConfig
```

## Data Flow

```
Raw Data (CSV)
      │
      ▼
┌─────────────────┐
│  DataLoader     │ Load & Basic Validation
└────────┬────────┘
         │
         ▼
┌─────────────────────┐
│  DataProcessor      │ Quality Checks, Handle Missing
└────────┬────────────┘
         │
         ▼
┌──────────────────────────┐
│ FinancialMetricsCalc     │ Returns, Volatility, Spreads
└────────┬─────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│ Feature Selection & Scaling      │
└────────┬────────────────────────┘
         │
         ├─────────────────────────────┬──────────────────┬──────────────┐
         │                             │                  │              │
         ▼                             ▼                  ▼              ▼
    ZScoreDetector              IQRDetector         IsolationForest   LOFDetector
         │                             │                  │              │
         └─────────────────────────────┴──────────────────┴──────────────┘
                                       │
                                       ▼
                        ┌──────────────────────────┐
                        │ EnsembleAnomalyDetector  │
                        │ (Voting / Weighted)      │
                        └──────────┬───────────────┘
                                   │
         ┌─────────────────────────┼─────────────────────────┐
         │                         │                         │
         ▼                         ▼                         ▼
    PCAAnalyzer          CorrelationAnalyzer      AnomalyStatisticsAnalyzer
         │                         │                         │
         └─────────────────────────┼─────────────────────────┘
                                   │
                                   ▼
                        ┌──────────────────────┐
                        │ AnomalyVisualizer    │
                        │ (Plotly Charts)      │
                        └──────────┬───────────┘
                                   │
         ┌─────────────────────────┴─────────────────────────┐
         │                                                   │
         ▼                                                   ▼
    CSV Export                                        HTML Visualizations
```

## Component Interaction Diagram

```
┌──────────────────────────────────────────────────────────────┐
│         MarketAnomalyDetectionPipeline (Orchestrator)        │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Configuration (PipelineConfig)                         │ │
│  └────────────────────────────────────────────────────────┘ │
│                        │                                    │
│  ┌─────────┐           │           ┌─────────────┐         │
│  │ DataOps │◄──────────┴──────────►│ DetectionOps│         │
│  └────┬────┘                       └──────┬──────┘         │
│       │                                    │                │
│       │  ┌──────────────┐  ┌──────────────────┐            │
│       └─►│ DataLoader   │  │ ZScoreDetector   │            │
│          │ DataProcessor│  │ IQRDetector      │            │
│          │ MetricsCalc  │  │ IForestDetector  │            │
│          └──────────────┘  │ LOFDetector      │            │
│                             │ EnsembleDetector│            │
│                             └──────────────────┘            │
│                                    │                        │
│  ┌──────────────┐                  │                        │
│  │ AnalysisOps  │◄─────────────────┘                        │
│  └────┬─────────┘                                           │
│       │                                                      │
│       │  ┌──────────────┐                                   │
│       └─►│ PCAAnalyzer  │                                   │
│          │ CorrAnalyzer │                                   │
│          │ StatsAnalyzer│                                   │
│          └──────────────┘                                   │
│                │                                            │
│                ▼                                            │
│       ┌────────────────────┐                                │
│       │ AnomalyVisualizer  │                                │
│       └────────────────────┘                                │
│                │                                            │
│  ┌─────────────┴─────────────┐                              │
│  │                           │                              │
│  ▼                           ▼                              │
│ CSV                    HTML Visualizations                  │
└──────────────────────────────────────────────────────────────┘
```

## Detector Comparison Matrix

```
┌──────────────────┬──────────┬──────────┬──────────┬──────────┐
│ Detector         │ Speed    │ Memory   │ Scalable │ Type     │
├──────────────────┼──────────┼──────────┼──────────┼──────────┤
│ ZScore           │ ████████ │ ████████ │ ████████ │ Distance │
│ IQR              │ ████████ │ ████████ │ ████████ │ Distance │
│ IsolationForest  │ ██████░░ │ ██████░░ │ ██████░░ │ Isolation│
│ LOF              │ ████░░░░ │ ████░░░░ │ ██████░░ │ Density  │
│ Ensemble         │ ████░░░░ │ ██████░░ │ ██████░░ │ Hybrid   │
└──────────────────┴──────────┴──────────┴──────────┴──────────┘

Speed:     Processing time (higher = faster)
Memory:    RAM consumption (higher = less)
Scalable:  Handles large datasets well (higher = better)
Type:      Statistical approach
```

## Configuration Hierarchy

```
PipelineConfig
│
├── DataConfig
│   ├── csv_path
│   ├── datetime_column
│   ├── price_columns[]
│   └── volume_columns[]
│
├── FeatureConfig
│   ├── feature_columns[]
│   ├── window_z
│   ├── window_iqr
│   └── roll_window
│
├── AnomalyDetectionConfig
│   ├── z_threshold
│   ├── contamination
│   ├── isolation_forest_estimators
│   ├── lof_neighbors
│   └── random_state
│
├── PCAConfig
│   ├── n_components
│   └── random_state
│
├── VisualizationConfig
│   ├── colors{}
│   ├── template
│   ├── figure_height
│   └── figure_width
│
└── output_dir
```

## Extension Points

```
To Add Custom Components:

1. Create New Detector:
   └── Inherit BaseAnomalyDetector
       ├── Implement fit()
       └── Implement detect() → (flags, scores)

2. Create New Feature Calculator:
   └── Inherit BaseFeatureCalculator
       └── Implement calculate(df) → df_with_features

3. Create New Analyzer:
   └── Inherit BaseAnalyzer
       └── Implement analyze(df) → results_dict

4. Create New Pipeline:
   └── Inherit BasePipeline
       └── Implement run(data) → results_dict
```

## Execution Flow

```
pipeline = MarketAnomalyDetectionPipeline(config)
│
└─ pipeline.run()
   │
   ├─ Step 1: Load data
   │  └─ DataLoader.load() → df_raw
   │
   ├─ Step 2: Process data
   │  └─ DataProcessor.calculate(df_raw) → df_processed
   │
   ├─ Step 3: Engineer features
   │  └─ FinancialMetricsCalculator.calculate() → df_featured
   │
   ├─ Step 4: Prepare model data
   │  └─ Select features, drop NaN → df_model
   │
   ├─ Step 5: Run individual detectors
   │  ├─ ZScoreDetector.fit_detect() → flags, scores
   │  ├─ IQRDetector.fit_detect() → flags, scores
   │  ├─ IsolationForestDetector.fit_detect() → flags, scores
   │  └─ LOFDetector.fit_detect() → flags, scores
   │
   ├─ Step 6: Ensemble combination
   │  └─ EnsembleAnomalyDetector.fit_detect() → final_flags, final_scores
   │
   ├─ Step 7: PCA analysis
   │  └─ PCAAnalyzer.analyze() → pca_results
   │
   ├─ Step 8: Correlation analysis
   │  └─ CorrelationAnalyzer.analyze() → corr_results
   │
   ├─ Step 9: Statistics
   │  └─ AnomalyStatisticsAnalyzer.analyze() → stats
   │
   ├─ Step 10: Visualizations
   │  ├─ AnomalyVisualizer.plot_price_with_anomalies()
   │  ├─ AnomalyVisualizer.plot_pca_scatter()
   │  ├─ AnomalyVisualizer.plot_anomaly_score_distribution()
   │  └─ AnomalyVisualizer.plot_correlation_heatmap()
   │
   └─ Return complete results dictionary
```

## Module Dependencies

```
main.py
└── PipelineConfig
└── MarketAnomalyDetectionPipeline
    ├── DataLoader
    ├── DataProcessor
    ├── FinancialMetricsCalculator
    ├── ZScoreDetector
    ├── IQRDetector
    ├── IsolationForestDetector
    ├── LOFDetector
    ├── EnsembleAnomalyDetector
    ├── PCAAnalyzer
    ├── CorrelationAnalyzer
    ├── AnomalyStatisticsAnalyzer
    └── AnomalyVisualizer
```

## Design Rationale

| Decision | Reason |
|----------|--------|
| Abstract Base Classes | Enable polymorphism and easy extension |
| Dataclass Config | Type-safe, immutable configuration |
| Dependency Injection | Loose coupling, testability |
| Single Responsibility | Easier debugging and maintenance |
| Composition over Inheritance | Flexible pipeline assembly |
| Factory Pattern for Detectors | Easy swapping/adding new methods |
| Plotly for Viz | Interactive, shareable HTML charts |
| Separate Analysis Classes | Reusability, clean separation |
| Pipeline Orchestrator | Centralized workflow management |
