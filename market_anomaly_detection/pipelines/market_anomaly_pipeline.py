"""
Complete Market Anomaly Detection Pipeline
"""
import json
import logging
from dataclasses import asdict
from pathlib import Path
import pandas as pd
import numpy as np
from typing import Dict, Any
from sklearn.preprocessing import StandardScaler
import joblib

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
    
    def __init__(self, config: PipelineConfig = None, logger: logging.Logger | None = None):
        """Initialize pipeline components and detectors."""
        super().__init__("MarketAnomalyDetectionPipeline")
        self.config = config or PipelineConfig()
        self.logger = logger or logging.getLogger(__name__)
        
        # Initialize components
        self.data_loader = DataLoader(self.config.data.csv_path, logger=self.logger)
        self.data_processor = DataProcessor(
            required_columns=self.config.data.required_columns,
            missing_value_strategy=self.config.data.missing_value_strategy,
            logger=self.logger,
        )
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
        self.ensemble_detector = EnsembleAnomalyDetector(
            self.detectors,
            method="voting",
            contamination=self.config.anomaly_detection.contamination,
        )
        
        self.df_raw = None
        self.df_processed = None
        self.df_featured = None
        self.df_model = None
        self.scaler = None
        
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
        
        self.logger.info("MARKET ANOMALY DETECTION PIPELINE")
        
        # Step 1: Load data
        self.logger.info("[Step 1] Loading data...")
        if data is None:
            self.df_raw = self.data_loader.load()
        else:
            self.df_raw = data.copy()
        
        # Step 2: Data processing
        self.logger.info("[Step 2] Processing data...")
        self.df_processed = self.data_processor.calculate(self.df_raw)
        
        # Step 3: Feature engineering
        self.logger.info("[Step 3] Engineering features...")
        self.df_featured = self.metrics_calculator.calculate(self.df_processed)
        
        # Step 4: Prepare model data
        self.logger.info("[Step 4] Preparing model data...")
        feature_cols = self.config.features.feature_columns
        valid_cols = [c for c in feature_cols if c in self.df_featured.columns]
        self.df_model = self.df_featured.dropna(subset=valid_cols).copy().reset_index(drop=True)
        
        # Step 5: Anomaly detection
        self.logger.info("[Step 5] Running anomaly detectors...")
        X = self.df_model[valid_cols].values
        self.logger.info("  Data shape before scaling: %s", X.shape)
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        self.scaler = scaler
        self.logger.info("  Data shape after scaling: %s", X_scaled.shape)
        
        self.results['detector_results'] = {}
        for detector in self.detectors:
            flags, scores = detector.fit_detect(X_scaled)
            self.logger.info(
                "  %s: flags shape = %s, scores shape = %s",
                detector.name,
                flags.shape,
                scores.shape,
            )
            self.df_model[f'{detector.name}_flag'] = flags
            self.df_model[f'{detector.name}_score'] = scores
            self.results['detector_results'][detector.name] = (flags, scores)
        
        # Step 6: Ensemble detection
        self.logger.info("[Step 6] Creating ensemble model...")
        ensemble_flags, ensemble_scores = self.ensemble_detector.fit_detect(X_scaled)
        self.df_model['is_anomaly'] = ensemble_flags
        self.df_model['anomaly_score'] = ensemble_scores
        
        # Step 7: PCA analysis
        self.logger.info("[Step 7] Performing PCA analysis...")
        pca_results = self.pca_analyzer.analyze(self.df_model, valid_cols)
        self.results['pca'] = pca_results
        
        # Step 8: Correlation analysis
        self.logger.info("[Step 8] Analyzing correlations...")
        corr_results = self.correlation_analyzer.analyze(self.df_model, valid_cols)
        self.results['correlation'] = corr_results
        
        # Step 9: Anomaly statistics
        self.logger.info("[Step 9] Computing anomaly statistics...")
        stats_results = self.anomaly_stats.analyze(self.df_model, 'is_anomaly')
        self.results['anomaly_stats'] = stats_results
        
        # Step 10: Visualizations
        self.logger.info("[Step 10] Generating visualizations...")
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
        
        self.logger.info("PIPELINE COMPLETED SUCCESSFULLY")
        self.logger.info("Results Summary:")
        self.logger.info("  - Total Records: %s", stats_results["total_records"])
        self.logger.info("  - Anomalies Detected: %s", stats_results["anomaly_count"])
        self.logger.info("  - Anomaly Rate: %s%%", stats_results["anomaly_rate"])
        self.logger.info("  - PCA Components: %s", len(pca_results["explained_variance"]))
        self.logger.info(
            "  - Explained Variance: %s",
            [f"{v:.2%}" for v in pca_results["explained_variance"]],
        )
        
        return self.results

    def save_artifacts(self, output_dir: str | Path = "models") -> Path:
        """Save trained artifacts and metadata for reproducibility."""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save scaler used for model input
        if self.scaler is not None:
            joblib.dump(self.scaler, output_dir / "scaler.joblib")

        # Save PCA artifacts
        if self.pca_analyzer.pca is not None:
            joblib.dump(self.pca_analyzer.pca, output_dir / "pca.joblib")
        if getattr(self.pca_analyzer, "scaler", None) is not None:
            joblib.dump(self.pca_analyzer.scaler, output_dir / "pca_scaler.joblib")

        # Save detector models where available
        for detector in self.detectors:
            model = getattr(detector, "model", None)
            if model is None:
                continue
            name = detector.name.replace("Detector", "").lower()
            joblib.dump(model, output_dir / f"{name}.joblib")

        # Save configuration and summary metadata
        def _to_jsonable(value):
            """Convert values into JSON-serializable forms."""
            if isinstance(value, Path):
                return str(value)
            if isinstance(value, dict):
                return {k: _to_jsonable(v) for k, v in value.items()}
            if isinstance(value, list):
                return [_to_jsonable(v) for v in value]
            if isinstance(value, tuple):
                return [_to_jsonable(v) for v in value]
            return value

        config_dict = _to_jsonable(asdict(self.config))

        summary = {
            "records": int(self.results.get("anomaly_stats", {}).get("total_records", 0)),
            "anomalies": int(self.results.get("anomaly_stats", {}).get("anomaly_count", 0)),
            "anomaly_rate": float(self.results.get("anomaly_stats", {}).get("anomaly_rate", 0.0)),
            "pca_explained_variance": self.results.get("pca", {}).get("explained_variance", []),
        }

        with (output_dir / "config.json").open("w", encoding="utf-8") as f:
            json.dump(config_dict, f, indent=2)
        with (output_dir / "summary.json").open("w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)

        return output_dir
    
    def get_results(self) -> pd.DataFrame:
        """Get the complete results dataframe"""
        return self.df_model
    
    def export_results(self, output_path: str = None):
        """Export results to CSV"""
        if output_path is None:
            output_path = str(self.config.output_dir / "anomaly_detection_results.csv")
        
        self.df_model.to_csv(output_path, index=False)
        self.logger.info("Results exported to %s", output_path)
        
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
