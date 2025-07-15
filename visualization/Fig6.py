import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects

# ========== Plotting Parameters ==========
plt.rcParams['font.family'] = ['Arial']
plt.rcParams['axes.unicode_minus'] = False

fig, ax = plt.subplots(figsize=(6, 5), dpi=300)
plt.xticks([])
plt.yticks([])

# === Adjustable Parameters ===
bar_width = 2
fontsize = 15
label_fontsize = 20
title_fontsize = 20
alpha_val = 1
axis_linewidth = 1.5
tick_width = 1.5
legend_fontsize = 11
text_offset_x = -0.07
text_offset_y = 1.12
road_type = 'motorway'
year = '22'

# === Column names ===
pop_col = f'{year}pop'
residual_col = f'residual_{year}_{road_type}'

# === Load and prepare data ===
# You should load your own DataFrame here with columns: ['name', pop_col, residual_col, 'label']
df = pd.read_excel('your_file.xlsx')  # Replace with your own DataFrame
df = df[['name', pop_col, residual_col, 'label']]
df_sorted = df.sort_values(by=residual_col, ascending=False)

positive_df = df_sorted[df_sorted[residual_col] > 0].reset_index(drop=True)
negative_df = df_sorted[df_sorted[residual_col] <= 0].copy()
negative_df[residual_col] = np.abs(negative_df[residual_col])
negative_df = negative_df.reset_index(drop=True)

# === Color Maps ===
cmap_pos = plt.cm.Reds
cmap_neg = plt.cm.Greens

# === Plot Positive Residuals ===
ax.bar(
    range(len(positive_df)),
    positive_df[residual_col],
    align='center',
    width=bar_width,
    edgecolor='none',
    label='SAMIs$>$0',
    color=cmap_pos(positive_df[residual_col] / positive_df[residual_col].max()),
    alpha=alpha_val
)

# === Plot Negative Residuals ===
ax.bar(
    range(len(positive_df), len(df_sorted)),
    -negative_df[residual_col],
    align='center',
    width=bar_width,
    edgecolor='none',
    label='SAMIs$\leq$0',
    color=cmap_neg(negative_df[residual_col] / negative_df[residual_col].max()),
    alpha=alpha_val
)

# === Axis Styling ===
ax.axhline(y=0, color='r', linestyle='--', linewidth=1)
ax.set_xlabel(r'$Rank$', fontsize=fontsize)
ax.set_ylabel(r'$SAMI\,\, residuals\,\,(\xi)$', fontsize=fontsize, labelpad=2.5)
ax.text(250, positive_df[residual_col].max() - 0.1,
        f'Country - {road_type.capitalize()}', fontsize=title_fontsize)

ax.text(text_offset_x, text_offset_y, 'A',
        fontsize=label_fontsize + 5,
        transform=ax.transAxes,
        verticalalignment='top', horizontalalignment='left')

ax.set_xlim(0, len(df_sorted))

# === Legend ===
legend = ax.legend(loc='lower left', frameon=False, fontsize=legend_fontsize)
legend.legendHandles[0].set_color('red')
legend.legendHandles[1].set_color('green')

# === Ticks & Spines ===
for spine in ax.spines.values():
    spine.set_linewidth(axis_linewidth)
ax.xaxis.set_tick_params(length=2, width=tick_width, labelsize=12)
ax.yaxis.set_tick_params(length=2, width=tick_width, labelsize=12)

# === Output (optional) ===
# fig.patch.set_alpha(0.0)
# plt.savefig('output.pdf', dpi=300)
plt.show()