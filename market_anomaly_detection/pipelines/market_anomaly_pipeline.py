"""
Complete Market Anomaly Detection Pipeline
"""
import pandas as pd
import numpy as np
from typing import Dict, Any
from sklearn.preprocessing import StandardScaler

from market_anomaly_detection.config import PipelineConfig
from market_anomaly_detection.data.processor import DataLoader, DataProcessor, FinancialMetricsCalculator
from market_anomaly_detection.detectors.ensemble import (
    ZScoreDetector, IQRDetector, IsolationForestDetector, 
    LOFDetector, EnsembleAnomalyDetector
)
from market_anomaly_detection.analysis.pca_analyzer import PCAAnalyzer, CorrelationAnalyzer, AnomalyStatisticsAnalyzer
from market_anomaly_detection.visualization.plotter import AnomalyVisualizer
from market_anomaly_detection.base.detector import BasePipeline


class MarketAnomalyDetectionPipeline(BasePipeline):
    """Complete pipeline for market anomaly detection"""
    
    def __init__(self, config: PipelineConfig = None):
        super().__init__("MarketAnomalyDetectionPipeline")
        self.config = config or PipelineConfig()
        
        # Initialize components
        self.data_loader = DataLoader(self.config.data.csv_path)
        self.data_processor = DataProcessor()
        self.metrics_calculator = FinancialMetricsCalculator()
        self.pca_analyzer = PCAAnalyzer(
            n_components=self.config.pca.n_components,
            random_state=self.config.pca.random_state
        )
        self.correlation_analyzer = CorrelationAnalyzer()
        self.anomaly_stats = AnomalyStatisticsAnalyzer()
        self.visualizer = AnomalyVisualizer(self.config.visualization)
        
        # Initialize detectors
        self.detectors = self._initialize_detectors()
        self.ensemble_detector = EnsembleAnomalyDetector(self.detectors, method="voting")
        
        self.df_raw = None
        self.df_processed = None
        self.df_featured = None
        self.df_model = None
        
    def _initialize_detectors(self) -> list:
        """Initialize all anomaly detectors"""
        config = self.config.anomaly_detection
        return [
            ZScoreDetector(threshold=config.z_threshold, window=self.config.features.window_z),
            IQRDetector(window=self.config.features.window_iqr),
            IsolationForestDetector(
                n_estimators=config.isolation_forest_estimators,
                contamination=config.contamination,
                random_state=config.random_state
            ),
            LOFDetector(
                n_neighbors=config.lof_neighbors,
                contamination=config.contamination
            )
        ]
    
    def run(self, data: pd.DataFrame = None) -> Dict[str, Any]:
        """Execute the complete pipeline"""
        
        print("=" * 80)
        print("MARKET ANOMALY DETECTION PIPELINE")
        print("=" * 80)
        
        # Step 1: Load data
        print("\n[Step 1] Loading data...")
        if data is None:
            self.df_raw = self.data_loader.load()
        else:
            self.df_raw = data.copy()
        
        # Step 2: Data processing
        print("[Step 2] Processing data...")
        self.df_processed = self.data_processor.calculate(self.df_raw)
        
        # Step 3: Feature engineering
        print("[Step 3] Engineering features...")
        self.df_featured = self.metrics_calculator.calculate(self.df_processed)
        
        # Step 4: Prepare model data
        print("[Step 4] Preparing model data...")
        feature_cols = self.config.features.feature_columns
        valid_cols = [c for c in feature_cols if c in self.df_featured.columns]
        self.df_model = self.df_featured.dropna(subset=valid_cols).copy().reset_index(drop=True)
        
        # Step 5: Anomaly detection
        print("[Step 5] Running anomaly detectors...")
        X = self.df_model[valid_cols].values
        print(f"  Data shape before scaling: {X.shape}")
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        print(f"  Data shape after scaling: {X_scaled.shape}")
        
        self.results['detector_results'] = {}
        for detector in self.detectors:
            flags, scores = detector.fit_detect(X_scaled)
            print(f"  {detector.name}: flags shape = {flags.shape}, scores shape = {scores.shape}")
            self.df_model[f'{detector.name}_flag'] = flags
            self.df_model[f'{detector.name}_score'] = scores
            self.results['detector_results'][detector.name] = (flags, scores)
        
        # Step 6: Ensemble detection
        print("[Step 6] Creating ensemble model...")
        ensemble_flags, ensemble_scores = self.ensemble_detector.fit_detect(X_scaled)
        self.df_model['is_anomaly'] = ensemble_flags
        self.df_model['anomaly_score'] = ensemble_scores
        
        # Step 7: PCA analysis
        print("[Step 7] Performing PCA analysis...")
        pca_results = self.pca_analyzer.analyze(self.df_model, valid_cols)
        self.results['pca'] = pca_results
        
        # Step 8: Correlation analysis
        print("[Step 8] Analyzing correlations...")
        corr_results = self.correlation_analyzer.analyze(self.df_model, valid_cols)
        self.results['correlation'] = corr_results
        
        # Step 9: Anomaly statistics
        print("[Step 9] Computing anomaly statistics...")
        stats_results = self.anomaly_stats.analyze(self.df_model, 'is_anomaly')
        self.results['anomaly_stats'] = stats_results
        
        # Step 10: Visualizations
        print("[Step 10] Generating visualizations...")
        threshold = np.quantile(ensemble_scores, 0.99)
        
        self.results['visualizations'] = {
            'price_with_anomalies': self.visualizer.plot_price_with_anomalies(
                self.df_model, date_col='quote_datetime'
            ),
            'pca_scatter': self.visualizer.plot_pca_scatter(self.df_model),
            'score_distribution': self.visualizer.plot_anomaly_score_distribution(
                ensemble_scores, threshold=threshold
            ),
            'correlation_heatmap': self.visualizer.plot_correlation_heatmap(
                corr_results['correlation_matrix']
            )
        }
        
        print("\n" + "=" * 80)
        print("PIPELINE COMPLETED SUCCESSFULLY")
        print("=" * 80)
        print(f"\nResults Summary:")
        print(f"  - Total Records: {stats_results['total_records']}")
        print(f"  - Anomalies Detected: {stats_results['anomaly_count']}")
        print(f"  - Anomaly Rate: {stats_results['anomaly_rate']}%")
        print(f"  - PCA Components: {len(pca_results['explained_variance'])}")
        print(f"  - Explained Variance: {[f'{v:.2%}' for v in pca_results['explained_variance']]}")
        
        return self.results
    
    def get_results(self) -> pd.DataFrame:
        """Get the complete results dataframe"""
        return self.df_model
    
    def export_results(self, output_path: str = None):
        """Export results to CSV"""
        if output_path is None:
            output_path = str(self.config.output_dir / "anomaly_detection_results.csv")
        
        self.df_model.to_csv(output_path, index=False)
        print(f"Results exported to {output_path}")
        
        return output_path


def run_pipeline(csv_path: str = None, config: PipelineConfig = None) -> MarketAnomalyDetectionPipeline:
    """Helper function to run the pipeline"""
    if config is None:
        config = PipelineConfig()
    
    if csv_path:
        config.data.csv_path = csv_path
    
    pipeline = MarketAnomalyDetectionPipeline(config)
    pipeline.run()
    
    return pipeline
