# Plot Management System

This project includes a **toggle-based plot management system** with automatic git exclusion for output files.

## Setup Files

### 1. `.gitignore` (Git Exclusion)
Automatically excludes all output files from version control:
- `reports/` - All plot output folders
- `*.html` - Plotly HTML files
- `data/` - Data files
- Python cache and environment folders

**Status**: ✓ Created and active

### 2. `plot_manager.py` (Plot Toggle System)
Manages plot generation with on/off toggles for each visualization.

**Status**: ✓ Created and tested

```
✓ Plot Manager Initialized

===========================================================================
                        PLOT GENERATION TOGGLE LIST
===========================================================================

Output Directory: C:\Users\hh\Market-Anomaly-Detection\outputs\plots

Plot ID                   Status     Saved      Filename
---------------------------------------------------------------------------
pca_anomaly_scatter       ✓ ON       ○          pca_anomaly_scatter.html      
anomaly_scores_time       ✓ ON       ○          anomaly_scores_time.html      
ensemble_components       ✓ ON       ○          ensemble_components.html      
price_anomalies           ✓ ON       ○          price_anomalies.html
---------------------------------------------------------------------------
Enabled: 4/4 | Saved: 0
===========================================================================
```

## Usage in Jupyter Notebook

### Quick Start
```python
from plot_manager import PLOTS_CONFIG, PLOTS_DIR, save_plot, display_plot_status

# Show current status
display_plot_status()

# Disable a specific plot
toggle_plot('pca_anomaly_scatter', False)

# Enable it again
toggle_plot('pca_anomaly_scatter', True)
```

### In Your Plot Cells
Wrap plot generation with the toggle system:

```python
import plotly.graph_objects as go
from plot_manager import should_generate_plot, save_plot

if should_generate_plot('pca_anomaly_scatter'):
    fig = go.Figure()
    
    # Build your plot...
    fig.add_trace(...)
    fig.update_layout(...)
    
    # Save using the manager
    save_plot(fig, 'pca_anomaly_scatter')
    fig.show()
else:
    print('⊖ Skipped: PCA plot disabled')
```

## Plot Toggle Commands

### Display Current Status
```python
display_plot_status()
# Shows: Enabled/Disabled status, saved status, file paths
```

### Toggle Individual Plots
```python
toggle_plot('plot_id', True)   # Enable
toggle_plot('plot_id', False)  # Disable
```

### List Saved Plots
```python
from plot_manager import list_saved_plots
list_saved_plots()
```

## Available Plots

1. **pca_anomaly_scatter** - 2D PCA visualization of normal vs anomalous points
2. **anomaly_scores_time** - Time series of ensemble anomaly scores
3. **ensemble_components** - Isolation Forest vs LOF score scatter
4. **price_anomalies** - Price overlay with detected anomalies

## Directory Structure

```
Market-Anomaly-Detection/
├── .gitignore                 # Git ignore rules
├── plot_manager.py            # Plot management module
├── Phase1_EDA.ipynb           # Main notebook
├── data/
│   └── msft_hourly(in).csv
└── reports/                   # (ignored by git)
    └── plots/                 # (ignored by git)
        ├── pca_anomaly_scatter.html
        ├── anomaly_scores_time.html
        ├── ensemble_components.html
        └── price_anomalies.html
```

## How to Use in Your Notebook

### Step 1: Import at Top
```python
import sys
sys.path.insert(0, '.')
from plot_manager import PLOTS_CONFIG, PLOTS_DIR, save_plot, display_plot_status, should_generate_plot
```

### Step 2: Initialize Once
```python
# Displays current configuration
display_plot_status()
```

### Step 3: Manage Plots Before Generating
```python
# Turn off a plot you don't need
toggle_plot('ensemble_components', False)

# View updated status
display_plot_status()
```

### Step 4: Wrap Your Plotting Code
```python
if should_generate_plot('your_plot_id'):
    fig = go.Figure()
    # ... build plot ...
    save_plot(fig, 'your_plot_id')
    fig.show()
else:
    print(f'Skipped: Plot disabled')
```

## Benefits

✓ **Git-Safe**: Output files automatically ignored  
✓ **Selective Rendering**: Control which plots generate  
✓ **Automatic Saving**: Plots save to organized folder  
✓ **Trackable**: Metadata on all generated plots  
✓ **Scalable**: Easy to add new plots to the config

## Example Workflow

```python
# Initialize
from plot_manager import display_plot_status, toggle_plot, should_generate_plot, save_plot

# See what's available
display_plot_status()

# Disable expensive plots temporarily (e.g., t-SNE)
toggle_plot('ensemble_components', False)

# Run notebook cell by cell
# Plots matching toggle config will auto-save to reports/plots/

# Check what saved
display_plot_status()  # Shows ✓ next to saved files

# Re-enable disabled plots
toggle_plot('ensemble_components', True)
display_plot_status()
```

---

**Setup Status**: ✓ Complete  
- [x] `.gitignore` configured
- [x] `plot_manager.py` created and tested
- [x] Toggle functions ready to use
- [ ] Notebook cells updated (next step - add `from plot_manager import ...` to your plotting cells)
