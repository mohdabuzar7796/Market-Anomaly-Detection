"""
Plot Management & Toggle System for Market Anomaly Detection EDA
Handles plot generation, saving, and configuration
"""

from pathlib import Path
from datetime import datetime
import json

# Configuration of available plots
PLOTS_CONFIG = {
    'pca_anomaly_scatter': {
        'name': 'PCA Anomaly Scatter',
        'description': 'Cluster separation in PCA space',
        'enabled': True,
        'filename': 'pca_anomaly_scatter.html'
    },
    'anomaly_scores_time': {
        'name': 'Anomaly Scores Over Time',
        'description': 'Time series of ensemble anomaly scores',
        'enabled': True,
        'filename': 'anomaly_scores_time.html'
    },
    'ensemble_components': {
        'name': 'Ensemble Components',
        'description': 'Isolation Forest vs LOF score scatter',
        'enabled': True,
        'filename': 'ensemble_components.html'
    },
    'price_anomalies': {
        'name': 'Price with Anomalies',
        'description': 'Price overlay with detected anomalies',
        'enabled': True,
        'filename': 'price_anomalies.html'
    },
}

# Output directory
PLOTS_DIR = Path('outputs/plots')
PLOTS_DIR.mkdir(parents=True, exist_ok=True)
META_FILE = PLOTS_DIR / 'plots_metadata.json'


def display_plot_status():
    """Display current plot configuration and saved status"""
    print('\n' + '='*75)
    print('PLOT GENERATION TOGGLE LIST'.center(75))
    print('='*75)
    print(f'\nOutput Directory: {PLOTS_DIR.resolve()}\n')
    print(f'{"Plot ID":<25} {"Status":<10} {"Saved":<10} {"Filename":<30}')
    print('-'*75)
    
    for plot_id, cfg in PLOTS_CONFIG.items():
        status = '✓ ON' if cfg['enabled'] else '✗ OFF'
        saved_file = PLOTS_DIR / cfg['filename']
        saved = '✓' if saved_file.exists() else '○'
        print(f'{plot_id:<25} {status:<10} {saved:<10} {cfg["filename"]:<30}')
    
    print('-'*75)
    enabled_count = sum(1 for p in PLOTS_CONFIG.values() if p['enabled'])
    saved_count = len(list(PLOTS_DIR.glob('*.html')))
    print(f'Enabled: {enabled_count}/{len(PLOTS_CONFIG)} | Saved: {saved_count}')
    print('='*75 + '\n')


def toggle_plot(plot_id, enable):
    """Toggle a specific plot on/off"""
    if plot_id not in PLOTS_CONFIG:
        print(f'✗ Error: Plot "{plot_id}" not found')
        return False
    
    PLOTS_CONFIG[plot_id]['enabled'] = enable
    status_word = 'enabled' if enable else 'disabled'
    print(f'✓ {PLOTS_CONFIG[plot_id]["name"]}: {status_word}')
    return True


def should_generate_plot(plot_id):
    """Check if a plot should be generated"""
    return PLOTS_CONFIG.get(plot_id, {}).get('enabled', False)


def save_plot(fig, plot_id, prefix=''):
    """Save a Plotly figure to HTML file"""
    if not should_generate_plot(plot_id):
        print(f'⊖ Skipped: {PLOTS_CONFIG[plot_id]["name"]} (disabled)')
        return None
    
    filename = PLOTS_CONFIG[plot_id]['filename']
    if prefix:
        filename = f'{prefix}_{filename}'
    
    plot_file = PLOTS_DIR / filename
    fig.write_html(plot_file)
    
    # Update metadata
    metadata = {
        'plot_id': plot_id,
        'name': PLOTS_CONFIG[plot_id]['name'],
        'file': str(plot_file),
        'timestamp': datetime.now().isoformat(),
        'enabled': PLOTS_CONFIG[plot_id]['enabled']
    }
    
    print(f'✓ Saved: {plot_file.resolve()}')
    return plot_file


def list_saved_plots():
    """List all saved plot files"""
    html_files = sorted(PLOTS_DIR.glob('*.html'))
    if not html_files:
        print('No plots saved yet.')
        return []
    
    print(f'\nSaved Plots ({len(html_files)}):')
    print('-' * 60)
    for f in html_files:
        size_kb = f.stat().st_size / 1024
        print(f'  • {f.name:<40} ({size_kb:.1f} KB)')
    print('-' * 60 + '\n')
    return html_files


# Initialize on import
if __name__ == '__main__':
    print('✓ Plot Manager Initialized')
    display_plot_status()
