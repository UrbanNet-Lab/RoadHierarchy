import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

# Define hierarchical road types (first letter uppercase)
columns = ['metro', 'motorway*', 'primary', 'secondary', 'tertiary', 'residential*', 'footway']
road_types = ['Me'] + [s[0].upper() if s else '' for s in columns[1:]]

# Custom colormap (blue to orange gradient)
colors = [
    (57/255, 81/255, 162/255),
    (114/255, 170/255, 207/255),
    (202/255, 232/255, 242/255),
    (254/255, 251/255, 186/255),
    (253/255, 185/255, 107/255),
    (236/255, 93/255, 59/255)
]
cmap = LinearSegmentedColormap.from_list("custom_cmap", colors, N=256)

# Layout & formatting parameters
fig, axes = plt.subplots(2, 2, figsize=(12, 11))
a = 0.07
font = 30
fontsize = 18
shrink_size = 0.9
text_position_a = -a + 0.08
text_position_b = 1 + a - 0.07
text_a = text_position_a - 0.1
text_b = text_position_b + 0.1

# Labels for subplots
subplot_labels = ['B', 'C', 'E', 'F']

def plot_heatmap(matrix, ax, label, title, colorbar_offset):
    """Plot heatmap with formatted colorbar and annotations."""
    heatmap = sns.heatmap(
        matrix, annot=True, fmt='.3f', cmap=cmap, cbar=True, ax=ax,
        vmin=0, vmax=0.8, annot_kws={"fontsize": 12},
        cbar_kws={"shrink": shrink_size, 'ticks': np.arange(0, 0.9, 0.2)}
    )

    ax.set_xticklabels(road_types, fontsize=fontsize)
    ax.set_yticklabels(road_types, fontsize=fontsize)
    ax.set_xlabel('$Hierarchy$', fontsize=fontsize+3)
    ax.set_ylabel('$Hierarchy$', fontsize=fontsize+3)
    ax.set_title(title, fontsize=fontsize+3, y=1.01)

    # Set subplot label (e.g., B, C, E, F)
    ax.text(text_a, text_b, label, transform=ax.transAxes,
            fontsize=font, color='black', ha="left", va="top")

    # Move colorbar to custom position
    pos = ax.get_position()
    cbar = heatmap.collections[0].colorbar
    cbar.remove()
    cax = fig.add_axes([
        pos.x0 + pos.width + colorbar_offset[0],
        pos.y0 + colorbar_offset[1],
        0.02,
        pos.height + colorbar_offset[2]
    ])
    new_cbar = fig.colorbar(heatmap.collections[0], cax=cax, orientation='vertical')
    new_cbar.set_ticks(np.arange(0, 0.9, 0.2))
    new_cbar.ax.tick_params(labelsize=fontsize-2)

# Define the matrices
connecting_usa = np.array([...])   # Replace with your matrix
connecting_china = np.array([...]) # Replace with your matrix
parallel_usa = np.array([...])     # Replace with your matrix
parallel_china = np.array([...])   # Replace with your matrix

# Plot all four heatmaps
plot_heatmap(connecting_usa, axes[0, 0], subplot_labels[0], '$Connecting$', [0.035, 0.043, -0.044])
plot_heatmap(parallel_usa, axes[0, 1], subplot_labels[1], '$Parallel$', [0.083, 0.043, -0.044])
plot_heatmap(connecting_china, axes[1, 0], subplot_labels[2], '$Connecting$', [0.035, 0.0026, -0.045])
plot_heatmap(parallel_china, axes[1, 1], subplot_labels[3], '$Parallel$', [0.083, 0.0025, -0.045])

# Adjust spacing and show the plot
plt.subplots_adjust(wspace=0.55, hspace=0.5)
fig.patch.set_alpha(0.0)
plt.show()



import matplotlib.pyplot as plt
import numpy as np

# Prepare columns and display settings
columns = ['motorway*', 'primary', 'secondary', 'tertiary', 'residential*', 'footway']
legend_labels = [col[0].upper() for col in columns]

# Define color scheme (consistent order)
colors = [
    (57/255, 81/255, 162/255),
    (114/255, 170/255, 207/255),
    (202/255, 232/255, 242/255),
    (254/255, 251/255, 186/255),
    (253/255, 185/255, 107/255),
    (236/255, 93/255, 59/255)
]

# Subplot configuration: 2 rows × 3 columns
fig, axes = plt.subplots(2, 3, figsize=(16, 11), constrained_layout=False)

# General styling parameters
fontsize = 18
font = 30
bar_width = 0.7
years = usa_percentages_df['Year']  # Ensure 'Year' is a column
x = np.arange(len(years))

# Position of subplot label (A, B, etc.)
text_offset_x = -0.12
text_offset_y = 1.13
first_label_char = 'A'

### --- USA: Top Left Subplot ---
bottom = np.zeros(len(years))
for i, category in enumerate(columns):
    axes[0, 0].bar(x, usa_percentages_df[category], bottom=bottom, width=bar_width,
                   label=legend_labels[i], color=colors[i])
    bottom += np.array(usa_percentages_df[category])

axes[0, 0].set_ylabel('Percentage', fontsize=fontsize + 3)
axes[0, 0].set_xlabel('Year', fontsize=fontsize + 3)
axes[0, 0].set_xticks(x, years, fontsize=fontsize)
axes[0, 0].set_yticks(axes[0, 0].get_yticks(), fontsize=fontsize)
axes[0, 0].set_ylim(0, 1)
axes[0, 0].grid(False)
axes[0, 0].text(text_offset_x, text_offset_y, first_label_char, ha="left", va="top",
                transform=axes[0, 0].transAxes, fontsize=font, color='black')

# Legend for USA subplot (on the right)
legend = axes[0, 0].legend(
    bbox_to_anchor=(1, 0.5),
    loc='center left',
    frameon=False,
    fontsize=fontsize - 3,
    ncol=1
)
for handle in legend.legendHandles:
    handle.set_edgecolor('black')
    handle.set_linewidth(1)

### --- China: Bottom Left Subplot ---
bottom = np.zeros(len(years))
for i, category in enumerate(columns):
    axes[1, 0].bar(x, china_percentages_df[category], bottom=bottom, width=bar_width,
                   label=legend_labels[i], color=colors[i])
    bottom += np.array(china_percentages_df[category])

axes[1, 0].set_ylabel('Percentage', fontsize=fontsize + 3)
axes[1, 0].set_xlabel('Year', fontsize=fontsize + 3)
axes[1, 0].set_xticks(x, years, fontsize=fontsize)
axes[1, 0].set_yticks(axes[1, 0].get_yticks(), fontsize=fontsize)
axes[1, 0].set_ylim(0, 1)
axes[1, 0].grid(False)
axes[1, 0].text(text_offset_x, text_offset_y, chr(ord(first_label_char) + 3), ha="left", va="top",
                transform=axes[1, 0].transAxes, fontsize=font, color='black')

# Disable unused subplots
axes[0, 1].axis('off')
axes[1, 1].axis('off')
axes[0, 2].axis('off')
axes[1, 2].axis('off')

# Adjust layout
plt.subplots_adjust(hspace=0.5)
fig.patch.set_alpha(0.0)

# Save or show the plot
# plt.savefig('road_type_distribution_usa_china.pdf', dpi=300)
plt.show()