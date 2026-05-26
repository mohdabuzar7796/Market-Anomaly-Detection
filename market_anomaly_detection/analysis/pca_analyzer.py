"""
Analysis module for PCA and correlations
"""
import numpy as np
import pandas as pd
from typing import Dict, Tuple, Any
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from market_anomaly_detection.base.detector import BaseAnalyzer


class PCAAnalyzer(BaseAnalyzer):
    """Principal Component Analysis for dimensionality reduction"""
    
    def __init__(self, n_components: int = 2, random_state: int = 42):
        """Configure PCA component count and RNG seed."""
        super().__init__("PCAAnalyzer")
        self.n_components = n_components
        self.random_state = random_state
        self.pca = None
        self.scaler = StandardScaler()
        self.explained_variance = None
        self.components = None
        self.loadings_df = None
        
    def analyze(self, data: pd.DataFrame, feature_cols: list) -> Dict[str, Any]:
        """Perform PCA analysis"""
        # Clean data
        clean_data = data.dropna(subset=feature_cols).copy()
        
        # Scale features
        X_scaled = self.scaler.fit_transform(clean_data[feature_cols])
        
        # Fit PCA
        self.pca = PCA(n_components=self.n_components, random_state=self.random_state)
        X_pca = self.pca.fit_transform(X_scaled)
        
        # Store results
        self.explained_variance = self.pca.explained_variance_ratio_
        self.components = self.pca.components_
        
        # Create loadings dataframe
        self.loadings_df = pd.DataFrame(
            self.pca.components_.T,
            index=feature_cols,
            columns=[f'PC{i+1}' for i in range(self.n_components)]
        )
        
        # Find dominant variables
        dominant_vars = {}
        for i in range(self.n_components):
            dominant_idx = np.argmax(np.abs(self.loadings_df[f'PC{i+1}']))
            dominant_vars[f'PC{i+1}'] = feature_cols[dominant_idx]
        
        # Add PCA scores to original dataframe
        pca_cols = [f'pca{i+1}' for i in range(self.n_components)]
        for i, col in enumerate(pca_cols):
            data.loc[clean_data.index, col] = X_pca[:, i]
        
        self.analysis_results = {
            'pca_scores': X_pca,
            'explained_variance': self.explained_variance.tolist(),
            'cumulative_variance': np.cumsum(self.explained_variance).tolist(),
            'loadings': self.loadings_df,
            'dominant_variables': dominant_vars,
            'original_indices': clean_data.index
        }
        
        return self.analysis_results


class CorrelationAnalyzer(BaseAnalyzer):
    """Correlation analysis"""
    
    def __init__(self, method: str = 'spearman'):
        """Set the correlation method used for analysis."""
        super().__init__("CorrelationAnalyzer")
        self.method = method
        self.correlation_matrix = None
        
    def analyze(self, data: pd.DataFrame, feature_cols: list = None) -> Dict[str, Any]:
        """Compute correlation matrix"""
        if feature_cols is None:
            feature_cols = data.select_dtypes(include=[np.number]).columns.tolist()
        
        # Keep only existing columns
        valid_cols = [col for col in feature_cols if col in data.columns]
        
        # Compute correlation
        self.correlation_matrix = data[valid_cols].corr(method=self.method).round(3)
        
        # Find highly correlated features
        high_corr_pairs = []
        for i in range(len(self.correlation_matrix.columns)):
            for j in range(i+1, len(self.correlation_matrix.columns)):
                corr_value = self.correlation_matrix.iloc[i, j]
                if abs(corr_value) > 0.7:
                    high_corr_pairs.append({
                        'feature1': self.correlation_matrix.columns[i],
                        'feature2': self.correlation_matrix.columns[j],
                        'correlation': float(corr_value)
                    })
        
        self.analysis_results = {
            'correlation_matrix': self.correlation_matrix,
            'high_correlation_pairs': high_corr_pairs
        }
        
        return self.analysis_results


class AnomalyStatisticsAnalyzer(BaseAnalyzer):
    """Analyze anomaly detection statistics"""
    
    def __init__(self):
        """Initialize the anomaly statistics analyzer."""
        super().__init__("AnomalyStatisticsAnalyzer")
        
    def analyze(self, data: pd.DataFrame, anomaly_col: str = 'is_anomaly') -> Dict[str, Any]:
        """Analyze anomaly statistics"""
        if anomaly_col not in data.columns:
            raise ValueError(f"Column '{anomaly_col}' not found in data")
        
        anomaly_count = int(data[anomaly_col].sum())
        total_count = len(data)
        anomaly_rate = (anomaly_count / total_count) * 100
        
        self.analysis_results = {
            'total_records': total_count,
            'anomaly_count': anomaly_count,
            'normal_count': total_count - anomaly_count,
            'anomaly_rate': round(anomaly_rate, 2),
            'normal_rate': round(100 - anomaly_rate, 2)
        }
        
        return self.analysis_results
