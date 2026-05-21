import json
import os

notebook_path = r'notebooks/Phase1_EDA_CORRECTED.ipynb'

if not os.path.exists(notebook_path):
    print(f"Error: {notebook_path} not found.")
    exit(1)

with open(notebook_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

new_code = [
    "import importlib\n",
    "import market_anomaly_detection.pipelines.market_anomaly_pipeline\n",
    "import market_anomaly_detection.utils.data_loader\n",
    "import market_anomaly_detection.models.anomaly_detector\n",
    "import market_anomaly_detection.visualization.visualizer\n",
    "importlib.reload(src.utils.data_loader)\n",
    "importlib.reload(src.models.anomaly_detector)\n",
    "importlib.reload(src.visualization.visualizer)\n",
    "importlib.reload(src.pipelines.market_anomaly_pipeline)\n",
    "from market_anomaly_detection.pipelines.market_anomaly_pipeline import MarketAnomalyPipeline\n",
    "\n",
    "# 1. Create pipeline with default config\n",
    "pipeline = MarketAnomalyPipeline()\n",
    "\n",
    "# 2. Run both default and custom configuration examples\n",
    "print(\"--- Running default configuration ---\")\n",
    "results_default = pipeline.run_pipeline()\n",
    "\n",
    "print(\"\\n--- Running custom configuration (contamination=0.01) ---\")\n",
    "results_custom = pipeline.run_pipeline(contamination=0.01)\n",
    "\n",
    "# 3. Print summary statistics\n",
    "def print_summary(results, label):\n",
    "    df = results['data']\n",
    "    anomalies_count = df['is_anomaly'].sum()\n",
    "    print(f\"Summary for {label}:\")\n",
    "    print(f\"  Total data points: {len(df)}\")\n",
    "    print(f\"  Anomalies detected: {anomalies_count} ({anomalies_count/len(df)*100:.2f}%)\")\n",
    "\n",
    "print_summary(results_default, \"Default Config\")\n",
    "print_summary(results_custom, \"Custom Config (0.01 contamination)\")\n"
]

found = False
for cell in nb['cells']:
    if cell['cell_type'] == 'code':
        source = "".join(cell['source'])
        if "from market_anomaly_detection.pipelines.market_anomaly_pipeline import" in source:
            cell['source'] = new_code
            found = True
            break

if found:
    with open(notebook_path, 'w', encoding='utf-8') as f:
        json.dump(nb, f, indent=1)
    print("Successfully updated the notebook.")
else:
    print("Target cell not found in the notebook.")
