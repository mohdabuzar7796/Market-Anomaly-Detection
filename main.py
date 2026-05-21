"""
Market Anomaly Detection Pipeline - Main Entry Point
"""
from market_anomaly_detection.config import PipelineConfig
from market_anomaly_detection.pipelines.market_anomaly_pipeline import MarketAnomalyDetectionPipeline
import plotly.io as pio


def main():
    """Main execution function"""
    
    # Initialize configuration
    config = PipelineConfig()
    
    # Create and run pipeline
    pipeline = MarketAnomalyDetectionPipeline(config)
    results = pipeline.run()
    
    # Export results
    output_csv = pipeline.export_results()
    print(f"\nResults saved to: {output_csv}")
    
    # Display visualizations
    print("\nGenerating visualizations...")
    visualizations = results['visualizations']
    
    for viz_name, fig in visualizations.items():
        output_html = str(config.output_dir / f"{viz_name}.html")
        fig.write_html(output_html)
        print(f"  - {viz_name}: {output_html}")
    
    # Print statistics
    stats = results['anomaly_stats']
    print(f"\n{'Anomaly Detection Statistics':^60}")
    print("-" * 60)
    print(f"Total Records:        {stats['total_records']:>10}")
    print(f"Normal Points:        {stats['normal_count']:>10}")
    print(f"Anomalies Detected:   {stats['anomaly_count']:>10}")
    print(f"Anomaly Rate:         {stats['anomaly_rate']:>9.2f}%")
    
    # Print PCA information
    pca_results = results['pca']
    print(f"\n{'PCA Analysis':^60}")
    print("-" * 60)
    for i, var in enumerate(pca_results['explained_variance']):
        print(f"PC{i+1} Explained Variance: {var:>8.2%}")
    print(f"Cumulative Variance:  {pca_results['cumulative_variance'][-1]:>8.2%}")
    
    print("\n" + "=" * 60)
    print("PIPELINE EXECUTION COMPLETED")
    print("=" * 60)
    
    return pipeline


if __name__ == "__main__":
    pipeline = main()
