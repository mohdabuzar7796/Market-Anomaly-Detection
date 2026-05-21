"""
Visualization module for market anomaly detection
"""
import plotly.graph_objects as go
import plotly.figure_factory as ff
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, Optional
from market_anomaly_detection.config import VisualizationConfig


class AnomalyVisualizer:
    """Visualizations for anomaly detection results"""
    
    def __init__(self, config: VisualizationConfig = None):
        self.config = config or VisualizationConfig()
        
    def plot_price_with_anomalies(self, data: pd.DataFrame, 
                                  date_col: str = 'quote_datetime',
                                  price_col: str = 'close',
                                  anomaly_col: str = 'is_anomaly',
                                  title: str = "Price with Anomalies") -> go.Figure:
        """Plot price time series with anomalies highlighted"""
        
        normal = data[data[anomaly_col] == 0]
        anomalies = data[data[anomaly_col] == 1]
        
        fig = go.Figure()
        
        # Normal price line
        fig.add_trace(go.Scatter(
            x=normal[date_col],
            y=normal[price_col],
            mode='lines',
            name='Price',
            line=dict(color=self.config.colors['price'], width=1),
            opacity=0.7
        ))
        
        # Anomaly markers
        fig.add_trace(go.Scatter(
            x=anomalies[date_col],
            y=anomalies[price_col],
            mode='markers',
            name='Anomalies',
            marker=dict(color=self.config.colors['anomaly'], size=8, symbol='diamond')
        ))
        
        fig.update_layout(
            title=title,
            xaxis_title='Date',
            yaxis_title='Price',
            template=self.config.template,
            hovermode='x unified',
            height=self.config.figure_height
        )
        
        return fig
    
    def plot_pca_scatter(self, data: pd.DataFrame,
                        pca1_col: str = 'pca1',
                        pca2_col: str = 'pca2',
                        anomaly_col: str = 'is_anomaly',
                        title: str = "PCA Scatter: Anomaly Clusters") -> go.Figure:
        """Plot PCA scatter with anomaly highlighting"""
        
        normal = data[data[anomaly_col] == 0]
        anomalies = data[data[anomaly_col] == 1]
        
        fig = go.Figure()
        
        # Normal points
        fig.add_trace(go.Scatter(
            x=normal[pca1_col],
            y=normal[pca2_col],
            mode='markers',
            name='Normal',
            marker=dict(color=self.config.colors['normal'], size=6, opacity=0.4)
        ))
        
        # Anomaly points
        fig.add_trace(go.Scatter(
            x=anomalies[pca1_col],
            y=anomalies[pca2_col],
            mode='markers',
            name='Anomaly',
            marker=dict(color=self.config.colors['anomaly'], size=8, symbol='diamond', opacity=1.0)
        ))
        
        fig.update_layout(
            title=title,
            xaxis_title='PCA Component 1',
            yaxis_title='PCA Component 2',
            template=self.config.template,
            hovermode='closest',
            height=self.config.figure_height
        )
        
        return fig
    
    def plot_anomaly_score_distribution(self, scores: np.ndarray,
                                        threshold: float = None,
                                        title: str = "Anomaly Score Distribution") -> go.Figure:
        """Plot distribution of anomaly scores"""
        
        fig = go.Figure()
        
        fig.add_trace(go.Histogram(
            x=scores,
            nbinsx=50,
            marker_color=self.config.colors['price'],
            opacity=0.7,
            name='Score Distribution'
        ))
        
        if threshold is not None:
            fig.add_vline(
                x=threshold,
                line_dash="dash",
                line_color=self.config.colors['anomaly'],
                annotation_text=f'Threshold ({threshold:.2f})'
            )
        
        fig.update_layout(
            title=title,
            xaxis_title='Anomaly Score',
            yaxis_title='Frequency',
            template=self.config.template,
            showlegend=False,
            height=self.config.figure_height
        )
        
        return fig
    
    def plot_correlation_heatmap(self, correlation_matrix: pd.DataFrame,
                                title: str = "Feature Correlation Matrix") -> go.Figure:
        """Plot correlation matrix heatmap"""
        
        fig = ff.create_annotated_heatmap(
            z=correlation_matrix.values,
            x=list(correlation_matrix.columns),
            y=list(correlation_matrix.index),
            colorscale="RdBu_r",
            showscale=True
        )
        
        fig.update_layout(
            title=title,
            template=self.config.template,
            height=700
        )
        
        return fig
    
    def plot_multi_detector_comparison(self, results: Dict[str, np.ndarray],
                                       data: pd.DataFrame,
                                       date_col: str = 'quote_datetime',
                                       price_col: str = 'close',
                                       title: str = "Multi-Detector Comparison") -> go.Figure:
        """Compare multiple detectors side by side"""
        
        n_detectors = len(results)
        fig = make_subplots(
            rows=n_detectors,
            cols=1,
            shared_xaxes=True,
            subplot_titles=list(results.keys())
        )
        
        for i, (detector_name, flags) in enumerate(results.items(), 1):
            anomalies = data[flags == 1]
            
            fig.add_trace(
                go.Scatter(
                    x=data[date_col],
                    y=data[price_col],
                    mode='lines',
                    line=dict(color=self.config.colors['normal'], width=0.5),
                    opacity=0.5,
                    showlegend=False
                ),
                row=i, col=1
            )
            
            fig.add_trace(
                go.Scatter(
                    x=anomalies[date_col],
                    y=anomalies[price_col],
                    mode='markers',
                    marker=dict(color=self.config.colors['anomaly'], size=5),
                    name=detector_name
                ),
                row=i, col=1
            )
        
        fig.update_layout(
            title=title,
            height=300 * n_detectors,
            showlegend=True,
            template=self.config.template
        )
        
        return fig
