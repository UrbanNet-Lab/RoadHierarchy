import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Radar chart settings
radar_min = -0.8
radar_max = 0.6
colors = ['orange', 'lightcoral', 'yellow', 'green']
tick_num = 4
tick_label_size = 11
label_fontsize = 20
title_fontsize = 40

# Offset for subplot labeling (A, B, etc.)
text_offset_x = -0.07
text_offset_y = 1.12
label_text = 'B'

# Road type labels (adjustable)
road_labels = ['Motorway', 'Primary', 'Secondary', 'Tertiary', 'Residential', 'Footway']

# Angles for radar chart
angles = np.linspace(0, 2 * np.pi, len(road_labels), endpoint=False).tolist()
angles += angles[:1]

# Load your DataFrame (ensure it includes a 'label' column and numerical columns for radar)
# Example structure: ['label', 'Motorway', 'Primary', ..., 'Footway']
# Replace with your actual DataFrame loading method
china_residual = pd.read_excel('your_file.xlsx')  # Placeholder
china_cluster_means = china_residual.groupby('label').mean()
zero_line = [0] * len(road_labels) + [0]

# Set up figure with 4 subplots (3 radar charts + 1 heatmap)
fig, axes = plt.subplots(nrows=1, ncols=4, figsize=(18, 4.5), subplot_kw={'projection': 'polar'})

# List of cluster indices to plot (adjust if needed)
china_indices = [0, 1, 2]
china_matrix = []

# Plot radar charts for each selected cluster
for i, cluster_idx in enumerate(china_indices):
    ax = axes[i]
    cluster_id = cluster_idx + 1

    if cluster_id in china_cluster_means.index:
        values = china_cluster_means.loc[cluster_id].values
        values = np.append(values, values[0])
        china_matrix.append(values)

        ax.fill(angles, values, alpha=0.2, color=colors[i])
        ax.plot(angles, zero_line, linestyle='--', color='red', linewidth=1, label='SAMI = 0')
        ax.set_rlim(radar_min, radar_max)
        ax.set_thetagrids(np.degrees(angles[:-1]), [])

        # Draw axis ticks
        ticks = np.linspace(radar_min, radar_max, tick_num)
        for angle in np.linspace(0, 2 * np.pi, len(road_labels), endpoint=False):
            for tick in ticks[1:]:
                ax.text(angle, tick, f'{tick:.2f}', ha='center', va='center', fontsize=tick_label_size)

        # Draw outer labels
        for angle, label in zip(angles, road_labels):
            ax.text(angle, radar_max + 0.35, label,
                    rotation=np.degrees(angle) - 90, ha='center', va='center')

        ax.set_yticklabels([])
        ax.spines['polar'].set_visible(False)
        ax.grid(True, color='black')
        ax.yaxis.set_visible(False)

        # Add subplot label
        if i == 0:
            ax.text(text_offset_x, text_offset_y, label_text, ha='left', va='top',
                    transform=ax.transAxes, fontsize=title_fontsize, color='black')
    else:
        ax.axis('off')

# Example: Define usa_matrix for cosine similarity comparison
# Must be a list of vectors with same dimension as china_matrix
# Replace this with your actual matrix
usa_matrix = np.random.rand(4, len(road_labels) + 1)  # Placeholder

# Cosine similarity function
def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# Compute similarity matrix
similarity = []
for china_vec in china_matrix:
    row = [cosine_similarity(china_vec, usa_vec) for usa_vec in usa_matrix]
    similarity.append(row)

# Plot heatmap
axes[3].axis('off')  # Hide the last polar plot
ax_heatmap = fig.add_subplot(1, 4, 4)
sns.heatmap(similarity,
            annot=True, cmap='Greens', fmt='.2f',
            xticklabels=['U1', 'U2', 'U3', 'U4'],
            yticklabels=['C1', 'C2', 'C3'],
            vmin=-1, vmax=1, alpha=0.5,
            cbar_kws={"orientation": "horizontal", "location": "top", "shrink": 0.95})
ax_heatmap.set_aspect('equal')
ax_heatmap.text(text_offset_x, text_offset_y, chr(ord(label_text) + 1), ha='left', va='top',
                transform=ax_heatmap.transAxes, fontsize=title_fontsize, color='black')

# Final layout and display
plt.tight_layout()
fig.patch.set_alpha(0.0)
plt.show()