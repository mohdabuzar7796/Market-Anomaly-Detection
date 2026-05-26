# Market Anomaly Detection

Industry-grade anomaly detection pipeline for MSFT hourly market data.

## Project Structure

- data/ - Raw and processed datasets
- docs/ - Documentation
- market_anomaly_detection/ - Source package
- models/ - Trained models and artifacts
- notebooks/ - Analysis notebooks
- references/ - Supporting materials
- reports/ - Generated analysis outputs

This layout follows the Cookiecutter Data Science structure.

## Quick Start

```powershell
# Run the pipeline
# On Windows PowerShell use:
.\make run
```

## Package Entry Points

```python
from market_anomaly_detection.modeling.predict import main
main()
```

Skip writing outputs:

```python
from market_anomaly_detection.modeling.predict import main
main(write_outputs=False)
```

CLI usage:

```powershell
python -m market_anomaly_detection.modeling.predict --no-output
```

## Data

Raw data lives in data/raw/. Use data/interim/ and data/processed/ for intermediate outputs.

## Notebooks

Notebooks are stored in notebooks/ and follow the naming convention:

```
<order>.<initials>-<short-description>.ipynb
```

## Artifacts

The pipeline writes trained artifacts and metadata into models/:

- scaler.joblib
- pca.joblib
- pca_scaler.joblib
- isolationforest.joblib
- lof.joblib
- config.json
- summary.json

## Outputs

See the generated outputs and plots index in [reports/outputs-index.md](reports/outputs-index.md).

## Development

```powershell
make format
make lint
```

## Environment (uv)

```powershell
# Create and sync a local environment
uv venv .venv
uv sync

# Add a dependency (and update the lockfile)
uv add <package>

# Update the lockfile only
uv lock
```
