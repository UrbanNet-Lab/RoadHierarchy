import numpy as np
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from matplotlib.ticker import MultipleLocator
from sklearn.metrics import r2_score

# ===========================
# Function Definitions
# ===========================

def compute_residuals(n, x_log, y_log, population):
    """Compute residuals for top-n and remaining cities based on population size"""
    sorted_indices = np.argsort(population)[::-1]
    top_n_indices = sorted_indices[:n]
    remaining_indices = sorted_indices[n:]

    residuals_top_n = np.array(y_log)[top_n_indices] - np.array(x_log)[top_n_indices]
    residuals_remaining = np.array(y_log)[remaining_indices] - np.array(x_log)[remaining_indices]

    mean_top_n = np.mean(np.abs(residuals_top_n))
    mean_remaining = np.mean(np.abs(residuals_remaining))

    print(f"Mean absolute residual (Top {n}): {mean_top_n}")
    print(f"Mean absolute residual (Others): {mean_remaining}")

    return (np.mean(residuals_top_n), mean_remaining,
            top_n_indices, remaining_indices,
            residuals_top_n, residuals_remaining)

def filter_zeros(bin_centers, hist):
    """Remove bins with zero count"""
    mask = hist != 0
    return bin_centers[mask], hist[mask]

def probability_density_constant(data, bins):
    """Compute probability density using fixed-width bins"""
    hist, edges = np.histogram(data, bins=bins)
    frequencies = hist / np.sum(hist)
    bin_centers = (edges[:-1] + edges[1:]) / 2
    return filter_zeros(bin_centers, frequencies)

# ===========================
# Plot Configuration
# ===========================

# Plotting settings
n = 50
alpha = 0.9
top_color = (253/255, 160/255, 107/255)
other_color = 'royalblue'
label_size = 15
tick_font_size = 13
text_size = 20
font_size_country = 19
font_weight = 400

# Axis limits for USA
usa_xlim = (1.9, 5.3)

# Axis limits for China
china_xlim = (1.4, 4.79)

# Inset settings
inset_x, inset_y = 0.363, 0.21
inset_width, inset_height = 0.125, 0.225
inset_xlim = (-1.8, 1.8)
inset_ylim = (0, 0.399)
inset_alpha = 0.2
inset_linewidth = 0.7
inset_font = 8

# Text label positioning
label_a = 'A'
label_offset_x = -0.07
label_offset_y = 1.12
country_label_offset = 0.04

# ===========================
# Create Figure
# ===========================

fig, ax = plt.subplots(1, 2, figsize=(10, 5), sharex=True, sharey=True)
plt.xticks([]); plt.yticks([])

# ===========================
# Plot: USA
# ===========================

ax = fig.add_subplot(1, 2, 1)

log_fhwa = np.log10(usa_yy)
log_osm = np.log10(usa_y4)

(mean_resid_top, mean_resid_others,
 top_idx, other_idx,
 residuals_top, residuals_other) = compute_residuals(n, log_fhwa, log_osm, usa_xx)

# Scatter plot
ax.scatter(log_fhwa[top_idx], log_osm[top_idx], color='none', edgecolors=top_color,
           alpha=alpha, marker='o', s=np.array(usa_xx)[top_idx] / 20000)
ax.scatter(log_fhwa[other_idx], log_osm[other_idx], color='none', edgecolors=other_color,
           alpha=alpha, marker='o', s=np.array(usa_xx)[other_idx] / 20000)
ax.plot(usa_xlim, usa_xlim, linestyle='--', color='grey', linewidth=3)

# Axes styling
for side in ['top', 'bottom', 'left', 'right']:
    ax.spines[side].set_linewidth(1.5)
ax.set_xlim(usa_xlim)
ax.set_ylim(usa_xlim)
ax.set_xlabel(r'$Road \, Length \, (FHWA)$', fontsize=label_size)
ax.set_ylabel(r'$Road \, Length \, (OSM)$', fontsize=label_size)
ax.tick_params(width=1.5, labelsize=tick_font_size + 1)

# R² annotation
print("R² (USA):", r2_score(usa_yy, usa_y4))

# Add panel label and country label
ax.text(label_offset_x, label_offset_y, label_a, fontsize=text_size + 5, transform=ax.transAxes)
ax.text(country_label_offset, 1 - country_label_offset, 'USA',
        fontsize=font_size_country, transform=ax.transAxes,
        fontproperties=FontProperties().set_weight(font_weight))

# Inset: Residual Distribution (USA)
inset_usa = fig.add_axes([inset_x, inset_y, inset_width, inset_height])
x_top, y_top = probability_density_constant(residuals_top, bins=8)
x_other, y_other = probability_density_constant(residuals_other, bins=13)
inset_usa.plot(x_top, y_top, color=top_color, linewidth=inset_linewidth, label=f'Top {n}')
inset_usa.plot(x_other, y_other, color=other_color, linewidth=inset_linewidth, label='Others')
inset_usa.axvline(x=0, linestyle='--', color='black', alpha=inset_alpha + 0.5)
inset_usa.fill_between(x_top, y_top, color=top_color, alpha=inset_alpha)
inset_usa.fill_between(x_other, y_other, color=other_color, alpha=inset_alpha)

inset_usa.set_xlabel(r'$\Delta$', fontsize=inset_font, labelpad=0)
inset_usa.set_ylabel(r'$P(\Delta)$', fontsize=inset_font, labelpad=0)
inset_usa.tick_params(labelsize=inset_font, direction='in')
inset_usa.set_xlim(inset_xlim)
inset_usa.set_ylim(inset_ylim)
inset_usa.yaxis.set_major_locator(MultipleLocator(0.15))
inset_usa.legend(loc='upper right', fontsize=inset_font - 2, frameon=False)

# ===========================
# Plot: China
# ===========================

ax = fig.add_subplot(1, 2, 2)

log_mohurd = np.log10(china_yy)
log_osm_c = np.log10(china_y2)

(mean_resid_top_c, mean_resid_others_c,
 top_idx_c, other_idx_c,
 residuals_top_c, residuals_other_c) = compute_residuals(n, log_mohurd, log_osm_c, china_xx)

# Scatter plot
ax.scatter(log_mohurd[top_idx_c], log_osm_c[top_idx_c], color='none', edgecolors=top_color,
           alpha=alpha, marker='o', s=np.array(china_xx)[top_idx_c] / 2)
ax.scatter(log_mohurd[other_idx_c], log_osm_c[other_idx_c], color='none', edgecolors=other_color,
           alpha=alpha, marker='o', s=np.array(china_xx)[other_idx_c] / 2)
ax.plot(china_xlim, china_xlim, linestyle='--', color='grey', linewidth=3)

# Axes styling
for side in ['top', 'bottom', 'left', 'right']:
    ax.spines[side].set_linewidth(1.5)
ax.set_xlim(china_xlim)
ax.set_ylim(china_xlim)
ax.set_xlabel(r'$Road \, Length \, (MoHURD)$', fontsize=label_size)
ax.tick_params(width=1.5, labelsize=tick_font_size + 1)

# R² annotation
print("R² (China):", r2_score(china_yy, china_y2))

# Add panel label and country label
ax.text(label_offset_x, label_offset_y, chr(ord(label_a) + 1), fontsize=text_size + 5, transform=ax.transAxes)
ax.text(country_label_offset, 1 - country_label_offset, 'China',
        fontsize=font_size_country, transform=ax.transAxes,
        fontproperties=FontProperties().set_weight(font_weight))

# Inset: Residual Distribution (China)
inset_china = fig.add_axes([inset_x + 0.48, inset_y, inset_width, inset_height])
x_top_c, y_top_c = probability_density_constant(residuals_top_c, bins=6)
x_other_c, y_other_c = probability_density_constant(residuals_other_c, bins=13)
inset_china.plot(x_top_c, y_top_c, color=top_color, linewidth=inset_linewidth, label=f'Top {n}')
inset_china.plot(x_other_c, y_other_c, color=other_color, linewidth=inset_linewidth, label='Others')
inset_china.axvline(x=0, linestyle='--', color='black', alpha=inset_alpha + 0.5)
inset_china.fill_between(x_top_c, y_top_c, color=top_color, alpha=inset_alpha)
inset_china.fill_between(x_other_c, y_other_c, color=other_color, alpha=inset_alpha)

inset_china.set_xlabel(r'$\Delta$', fontsize=inset_font, labelpad=0)
inset_china.set_ylabel(r'$P(\Delta)$', fontsize=inset_font, labelpad=0)
inset_china.tick_params(labelsize=inset_font, direction='in')
inset_china.set_xlim(inset_xlim)
inset_china.set_ylim(inset_ylim)
inset_china.yaxis.set_major_locator(MultipleLocator(0.15))
inset_china.legend(loc='upper right', fontsize=inset_font - 2, frameon=False)

# ===========================
# Save & Show
# ===========================

plt.tight_layout()
fig.patch.set_alpha(0.0)
plt.show()
