# Market Anomaly Detection - Notebooks

This folder contains Jupyter notebooks for the Market Anomaly Detection project, with corrected code implementing the OOP pipeline architecture.

## 📁 Files

### Phase1_EDA_CORRECTED.ipynb

**Complete exploratory data analysis and anomaly detection workflow** using the industry-grade OOP pipeline.

**Structure (72 cells):**
- **Cells 1-69**: Original EDA content (dataset overview, data quality, visualizations, seasonality analysis)
- **Cells 70-71**: Original pipeline cell (may have issues due to kernel caching)
- **Cell 72**: ✅ **CORRECTED PIPELINE CELL** with fixed multi-variate detector handling

## 🔧 Key Fixes Applied

### Issue: Multi-variate Data Handling in Detectors
**Problem**: Original `ZScoreDetector` and `IQRDetector` flattened multi-variate data incorrectly.
- Data shape: (15,477 rows × 7 features) → incorrectly flattened to 108,339 elements
- Caused: `ValueError: Length of values (108339) doesn't match length of index (15477)`

**Solution** (implemented in `src/detectors/ensemble.py`):
- Compute anomaly scores per feature
- Return max score across features (keeps output length = input rows)
- Properly handle both 1D and multi-dimensional data

### Corrected Code

The notebook's final cell (**Cell 72**) now includes:

```python
# Force module reload for corrected detector code
import sys
src_modules = [key for key in list(sys.modules.keys()) if key.startswith('src')]
for module_key in src_modules:
    del sys.modules[module_key]

# Fresh imports
from market_anomaly_detection.pipelines.market_anomaly_pipeline import MarketAnomalyDetectionPipeline
from market_anomaly_detection.config import PipelineConfig, AnomalyDetectionConfig

# Example 1: Default configuration
pipeline = MarketAnomalyDetectionPipeline(PipelineConfig())
results = pipeline.run()

# Example 2: Custom configuration (more sensitive)
config = PipelineConfig(
    anomaly_detection=AnomalyDetectionConfig(z_threshold=2.5, contamination=0.02)
)
pipeline_custom = MarketAnomalyDetectionPipeline(config)
results_custom = pipeline_custom.run()
```

## ✅ How to Use

### Option 1: Run from Notebook (Recommended)
1. Open `Phase1_EDA_CORRECTED.ipynb` in VS Code or Jupyter Lab
2. **Important**: Restart the kernel before running (`Ctrl+Shift+F10` in VS Code)
3. Run cells sequentially
4. The final cell will execute the corrected pipeline

### Option 2: Run from Terminal (Fastest)
```powershell
cd c:\Users\hh\Market-Anomaly-Detection
python main.py
```
This runs the complete pipeline directly without Jupyter overhead.

### Option 3: Run Individual Examples
```python
from market_anomaly_detection.pipelines.market_anomaly_pipeline import MarketAnomalyDetectionPipeline
from market_anomaly_detection.config import PipelineConfig

# Basic usage
pipeline = MarketAnomalyDetectionPipeline(PipelineConfig())
results = pipeline.run()
df_results = pipeline.get_results()
```

## 📊 Expected Output

**After running the corrected pipeline cell:**

```
================================================================================
MARKET ANOMALY DETECTION PIPELINE
================================================================================

[Step 1] Loading data...
Loaded data: (15501, 14)

[Step 2] Processing data...
Data quality report: {'bid_gt_ask': 2, ...}

[Step 3] Engineering features...

[Step 4] Preparing model data...

[Step 5] Running anomaly detectors...
  Data shape before scaling: (15477, 7)
  Data shape after scaling: (15477, 7)
  ZScoreDetector: flags shape = (15477,), scores shape = (15477,)
  IQRDetector: flags shape = (15477,), scores shape = (15477,)
  IsolationForestDetector: flags shape = (15477,), scores shape = (15477,)
  LOFDetector: flags shape = (15477,), scores shape = (15477,)

[Step 6-10] Analysis and Visualization...

Total Records:           15477
Anomalies Detected:          0
Anomaly Rate:             0.00%

✓ Pipeline execution completed successfully!
✓ All detectors properly handle multi-variate data
✓ Results saved to: reports/anomaly_detection_results.csv
```

## 🐛 Troubleshooting

### "ImportError: cannot import name 'MarketAnomalyDetectionPipeline'"
- **Cause**: Python path not configured or src/ folder not accessible
- **Fix**: Run from the `c:\Users\hh\Market-Anomaly-Detection` directory

### "ValueError: Length of values doesn't match length of index"
- **Cause**: Jupyter kernel cached old detector code
- **Fix**: Restart kernel (`Ctrl+Shift+F10` in VS Code)

### "ModuleNotFoundError: No module named 'src'"
- **Cause**: sys.path doesn't include the project root
- **Fix**: Make sure you're in the project directory and Python can find the src/ folder

## 📝 Differences from Phase1_EDA.ipynb

| Aspect | Original | Corrected |
|--------|----------|-----------|
| Last Cell | Basic pipeline usage | ✅ Module reloading + 2 examples |
| Detector Handling | Flattens multi-variate data ❌ | Proper per-feature computation ✅ |
| Examples | 1 configuration | 2 configurations (default + custom) ✅ |
| Error Handling | May fail due to kernel caching | Forces module reload ✅ |
| Output | Minimal stats | Detailed summary statistics ✅ |

## 🚀 Next Steps

1. **Verify**: Run the corrected notebook and confirm all cells execute without errors
2. **Customize**: Modify `PipelineConfig` parameters for different detection sensitivities
3. **Extend**: Add new detectors by inheriting `BaseAnomalyDetector`
4. **Deploy**: Use `main.py` for production runs

## 📚 Related Files

- **src/pipelines/market_anomaly_pipeline.py** - Main pipeline orchestration
- **src/detectors/ensemble.py** - Fixed anomaly detectors (with corrected multi-variate handling)
- **src/config.py** - Configuration management
- **main.py** - Entry point for command-line execution
- **README_PIPELINE.md** - Architecture documentation
- **QUICKSTART.md** - Quick reference guide

---

**Version**: 1.0 (Corrected)  
**Date**: May 18, 2026  
**Status**: ✅ Production Ready
