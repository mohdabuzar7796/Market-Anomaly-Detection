import json

# Load the notebook
with open(r'c:\Users\hh\Market-Anomaly-Detection\Phase1_EDA.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

# The fixed source code as a single string
fixed_code = """# Create interactive PCA scatter plot with high contrast
# Add 'is_anomaly' column to df_model if it doesn't exist
if 'is_anomaly' not in df_model.columns:
    df_model['is_anomaly'] = 0
    if 'combined_flag' in part.columns:
        df_model.loc[part.index, 'is_anomaly'] = part['combined_flag'].values

fig = go.Figure()

# Add Normal points - lighter, muted color
fig.add_trace(go.Scatter(
    x=df_model[df_model['is_anomaly'] == False]['pca1'],
    y=df_model[df_model['is_anomaly'] == False]['pca2'],
    mode='markers',
    name='Normal',
    marker=dict(color='#cbd5e1', size=6, opacity=0.4), # Muted slate color
    hovertemplate='PCA1: %{x:.2f}<br>PCA2: %{y:.2f}<extra></extra>'
))

# Add Anomaly points - darker, saturated color
fig.add_trace(go.Scatter(
    x=df_model[df_model['is_anomaly'] == True]['pca1'],
    y=df_model[df_model['is_anomaly'] == True]['pca2'],
    mode='markers',
    name='Anomaly',
    marker=dict(color='#1e293b', size=8, symbol='diamond', opacity=1.0), # Dark slate/navy color
    hovertemplate='<b>Anomaly</b><br>PCA1: %{x:.2f}<br>PCA2: %{y:.2f}<extra></extra>'
))

fig.update_layout(
    title='Cluster Separation in PCA Space: Anomaly Contrast (Interactive)',
    xaxis_title='PCA Component 1 (vol_24h)',
    yaxis_title='PCA Component 2 (log_return)',
    template='plotly_white',
    hovermode='closest',
    height=600,
    legend=dict(yanchor='top', y=0.99, xanchor='left', x=0.01)
)

fig.show()
"""

# Convert to source list format (notebook format)
source_lines = [line + '\n' for line in fixed_code.split('\n')]
if source_lines[-1] == '\n':  # Remove extra newline at end
    source_lines = source_lines[:-1]

# Find and update the cell with index 66
nb['cells'][66]['source'] = source_lines

# Save the notebook
with open(r'c:\Users\hh\Market-Anomaly-Detection\Phase1_EDA.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1)

print("Updated cell at index 66")
print("Verifying...")
# Verify
with open(r'c:\Users\hh\Market-Anomaly-Detection\Phase1_EDA.ipynb', 'r', encoding='utf-8') as f:
    nb2 = json.load(f)
    content = ''.join(nb2['cells'][66]['source'])
    lines = content.split('\n')[:8]
    for i, line in enumerate(lines, 1):
        print(f"{i}: {line}")
print("Notebook saved successfully")
