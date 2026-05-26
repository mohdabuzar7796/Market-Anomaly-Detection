"""
Market Anomaly Detection Pipeline - Usage Examples
"""
from market_anomaly_detection.config import PipelineConfig, DataConfig, FeatureConfig, AnomalyDetectionConfig
from market_anomaly_detection.pipelines.market_anomaly_pipeline import MarketAnomalyDetectionPipeline
from market_anomaly_detection.detectors.ensemble import ZScoreDetector, IQRDetector, IsolationForestDetector
from market_anomaly_detection.data.processor import DataLoader, FinancialMetricsCalculator
from market_anomaly_detection.analysis.pca_analyzer import PCAAnalyzer
from pathlib import Path
import pandas as pd


def example_basic_pipeline():
    """Example 1: Run basic pipeline with default configuration"""
    print("\n" + "="*80)
    print("EXAMPLE 1: Basic Pipeline with Default Configuration")
    print("="*80)
    
    # Create pipeline with default config
    pipeline = MarketAnomalyDetectionPipeline()
    results = pipeline.run()
    
    # Get results
    df_results = pipeline.get_results()
    print(f"\nResults shape: {df_results.shape}")
    print(f"Columns: {list(df_results.columns)}")
    
    return pipeline


def example_custom_configuration():
    """Example 2: Run pipeline with custom configuration"""
    print("\n" + "="*80)
    print("EXAMPLE 2: Pipeline with Custom Configuration")
    print("="*80)
    
    # Create custom config
    config = PipelineConfig(
        data=DataConfig(csv_path=Path("data/raw/msft_hourly(in).csv")),
        features=FeatureConfig(
            feature_columns=["spread_pct", "log_return", "vol_24h"],
            window_z=20,
            window_iqr=20
        ),
        anomaly_detection=AnomalyDetectionConfig(
            z_threshold=3,
            contamination=0.02,
            isolation_forest_estimators=300
        )
    )
    
    # Run pipeline
    pipeline = MarketAnomalyDetectionPipeline(config)
    results = pipeline.run()
    
    return pipeline


def example_individual_detectors():
    """Example 3: Use individual detectors"""
    print("\n" + "="*80)
    print("EXAMPLE 3: Using Individual Detectors")
    print("="*80)
    
    # Load data
    loader = DataLoader(Path("data/msft_hourly(in).csv"))
    df = loader.load()
    
    # Process data
    processor = DataLoader(Path("data/msft_hourly(in).csv"))
    df = processor.load()
    
    # Get sample data
    sample_data = df['close'].values[-1000:].reshape(-1, 1)
    
    # Initialize detectors
    z_score_detector = ZScoreDetector(threshold=3, window=30)
    iqr_detector = IQRDetector(window=30)
    
    # Run detectors
    z_flags, z_scores = z_score_detector.fit_detect(sample_data)
    iqr_flags, iqr_scores = iqr_detector.fit_detect(sample_data)
    
    print(f"\nZ-Score Detector Results:")
    print(f"  - Anomalies: {z_flags.sum()}")
    print(f"  - Mean Score: {z_scores.mean():.4f}")
    
    print(f"\nIQR Detector Results:")
    print(f"  - Anomalies: {iqr_flags.sum()}")
    print(f"  - Mean Score: {iqr_scores.mean():.4f}")


def example_feature_engineering():
    """Example 4: Feature engineering"""
    print("\n" + "="*80)
    print("EXAMPLE 4: Feature Engineering")
    print("="*80)
    
    # Load data
    loader = DataLoader(Path("data/msft_hourly(in).csv"))
    df = loader.load()
    
    # Calculate metrics
    metrics_calc = FinancialMetricsCalculator()
    df_featured = metrics_calc.calculate(df)
    
    feature_cols = ['return_1h', 'log_return', 'vol_6h', 'vol_24h', 'high_low_range']
    
    print(f"\nGenerated Features:")
    for col in feature_cols:
        if col in df_featured.columns:
            non_null = df_featured[col].notna().sum()
            mean = df_featured[col].mean()
            std = df_featured[col].std()
            print(f"  {col:20s}: mean={mean:8.6f}, std={std:8.6f}, non_null={non_null}")


def example_pca_analysis():
    """Example 5: PCA Analysis"""
    print("\n" + "="*80)
    print("EXAMPLE 5: PCA Analysis")
    print("="*80)
    
    # Load data
    loader = DataLoader(Path("data/msft_hourly(in).csv"))
    df = loader.load()
    
    # Feature engineering
    metrics_calc = FinancialMetricsCalculator()
    df_featured = metrics_calc.calculate(df)
    
    # PCA
    pca_analyzer = PCAAnalyzer(n_components=2)
    feature_cols = ["spread_pct", "log_return", "vol_24h", "high_low_range"]
    valid_cols = [c for c in feature_cols if c in df_featured.columns]
    
    pca_results = pca_analyzer.analyze(df_featured, valid_cols)
    
    print(f"\nPCA Results:")
    print(f"  - Explained Variance: {pca_results['explained_variance']}")
    print(f"  - Cumulative Variance: {pca_results['cumulative_variance']}")
    print(f"\nDominant Variables:")
    for pc, var in pca_results['dominant_variables'].items():
        print(f"  - {pc}: {var}")


def example_results_export():
    """Example 6: Export results"""
    print("\n" + "="*80)
    print("EXAMPLE 6: Export Results")
    print("="*80)
    
    # Run pipeline
    pipeline = MarketAnomalyDetectionPipeline()
    results = pipeline.run()
    
    # Export to CSV
    csv_path = pipeline.export_results()
    
    # Export visualizations
    config = PipelineConfig()
    visualizations = results['visualizations']
    
    for viz_name, fig in visualizations.items():
        output_html = str(config.output_dir / f"{viz_name}.html")
        fig.write_html(output_html)
        print(f"  - Saved: {output_html}")
    
    print(f"\nResults exported to: {csv_path}")


if __name__ == "__main__":
    print("\nMarket Anomaly Detection Pipeline - Usage Examples")
    print("="*80)
    
    # Run examples
    # example_basic_pipeline()
    # example_custom_configuration()
    # example_individual_detectors()
    # example_feature_engineering()
    # example_pca_analysis()
    # example_results_export()
    
    print("\nUncomment the examples you want to run in the if __name__ == '__main__' block")
