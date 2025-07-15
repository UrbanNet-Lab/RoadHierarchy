import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.ticker import MultipleLocator, FuncFormatter
from matplotlib.colors import ListedColormap

def plot_lisa_dual_maps(gdf, base_map, colors, colors_new, names_new, set_edgecolor):
    """
    Plot dual LISA cluster maps (e.g., motorway and footway) on USA map.

    Parameters:
    - gdf: GeoDataFrame containing LISA clustering results.
    - base_map: GeoDataFrame for national boundaries.
    - colors: List of colormap values.
    - colors_new: Colors for custom legend patches.
    - names_new: Labels for legend.
    - set_edgecolor: Function to determine edge color based on clustering.

    Returns:
    - Matplotlib figure
    """
    a = 0.07
    text_position_a = -a
    text_position_b = 1 + a + 0.05
    text_size = 20
    MultipleLocator_size_x = 20
    MultipleLocator_size_y = 10

    fig, axes = plt.subplots(1, 2, figsize=(9, 3.3), dpi=400)
    cmap = ListedColormap(colors)

    # Motorway map (left)
    gdf['Medgecolor'] = gdf.apply(lambda row: set_edgecolor(row, 'LISA_CL_M'), axis=1)
    base_map.plot(ax=axes[0], ec='gray', fc="white", linewidth=0.4)
    gdf.plot(column='LISA_CL_M', ax=axes[0], ec=gdf['Medgecolor'], linewidth=0.4,
             cmap=cmap, alpha=1, legend=False, categorical=True)
    axes[0].set_xlim(-132, -66)
    axes[0].set_ylim(23, 52)
    axes[0].xaxis.set_major_locator(MultipleLocator(MultipleLocator_size_x))
    axes[0].yaxis.set_major_locator(MultipleLocator(MultipleLocator_size_y))
    axes[0].xaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{abs(x):.0f}°{'E' if x >= 0 else 'W'}"))
    axes[0].yaxis.set_major_formatter(FuncFormatter(lambda y, _: f"{abs(y):.0f}°{'N' if y >= 0 else 'S'}"))
    axes[0].text(text_position_a, text_position_b, 'C', fontsize=text_size, transform=axes[0].transAxes)
    axes[0].text(-130.7, 32.3, "Motorway", fontsize=9)
    axes[0].legend([Patch(facecolor=color, edgecolor='gray', label=name, linewidth=0.5)
                    for color, name in zip(colors_new, names_new)],
                   loc='lower left', frameon=False, fontsize=7.5, handletextpad=0.8, labelspacing=0.25)

    # Footway map (right)
    gdf['Fedgecolor'] = gdf.apply(lambda row: set_edgecolor(row, 'LISA_CL_F'), axis=1)
    base_map.plot(ax=axes[1], ec='gray', fc="white", linewidth=0.4)
    gdf.plot(column='LISA_CL_F', ax=axes[1], ec=gdf['Fedgecolor'], linewidth=0.4,
             cmap=cmap, alpha=1, legend=False, categorical=True)
    axes[1].set_xlim(-132, -66)
    axes[1].set_ylim(23, 52)
    axes[1].xaxis.set_major_locator(MultipleLocator(MultipleLocator_size_x))
    axes[1].yaxis.set_major_locator(MultipleLocator(MultipleLocator_size_y))
    axes[1].xaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{abs(x):.0f}°{'E' if x >= 0 else 'W'}"))
    axes[1].yaxis.set_major_formatter(FuncFormatter(lambda y, _: f"{abs(y):.0f}°{'N' if y >= 0 else 'S'}"))
    axes[1].text(text_position_a, text_position_b, 'D', fontsize=text_size, transform=axes[1].transAxes)
    axes[1].text(-130.7, 32.3, "Footway", fontsize=10)
    axes[1].legend([Patch(facecolor=color, edgecolor='gray', label=name, linewidth=0.5)
                    for color, name in zip(colors_new, names_new)],
                   loc='lower left', frameon=False, fontsize=7.5, handletextpad=0.8, labelspacing=0.25)

    plt.tight_layout()
    fig.patch.set_alpha(0.0)
    return fig

import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
from shapely.geometry import Point
from sklearn.preprocessing import MinMaxScaler
from matplotlib.ticker import MultipleLocator, FuncFormatter

def plot_sami_distribution(base_map, sami_df, column, region_name, color_gt, color_le, label_pos, ax_extent):
    """
    Plot SAMI spatial distribution with categorized scatter points.

    Parameters:
    - base_map: GeoDataFrame of the country's boundary
    - sami_df: DataFrame with lat/lon and SAMI value (converted to GeoDataFrame internally)
    - column: Name of the residual/SAMI column (e.g. 'residual_22_motorway')
    - region_name: Title or label of the region (e.g. 'USA', 'China')
    - color_gt: Color for positive values (e.g. '#FB8402')
    - color_le: Color for negative values (e.g. '#68BED9')
    - label_pos: Coordinates for annotation
    - ax_extent: Tuple of (xlim, ylim)
    """
    k = 3
    size_coefficient = [0.125, 0.46875, 0.9375, 1.53125]
    s_conficient = 300

    # Convert to GeoDataFrame
    geometry = [Point(lon, lat) for lon, lat in zip(sami_df['lon'], sami_df['lat'])]
    gdf = gpd.GeoDataFrame(sami_df, geometry=geometry, crs="EPSG:4326")

    # Normalize population (optional)
    # scaler = MinMaxScaler(feature_range=(0.3, 1))
    # gdf['normalized_pop'] = scaler.fit_transform(gdf[[pop]])

    fig, ax = plt.subplots(figsize=(8, 5), dpi=300)
    base_map.to_crs(epsg=4326).plot(ax=ax, fc="white", ec="gray", linewidth=.8)

    # Positive SAMIs
    gt0 = gdf[gdf[column] > 0]
    max_val = gt0[column].max()
    bins_gt = [round(i * max_val / k, 2) for i in range(k+1)]
    gt0['group'] = pd.cut(gt0[column], bins_gt)

    for i, (group, subset) in enumerate(gt0.groupby('group')):
        if not subset.empty:
            subset.plot(ax=ax, color=color_gt, edgecolor='lightgray',
                        markersize=s_conficient * size_coefficient[i], alpha=1, lw=0.5)
        ax.scatter([], [], c=color_gt, s=s_conficient * size_coefficient[i],
                   label=f'{group.left:.2f} - {group.right:.2f}', ec="lightgray", alpha=0.8, lw=0.5)

    # Negative SAMIs
    le0 = gdf[gdf[column] <= 0]
    min_val = le0[column].min()
    bins_le = [round(min_val + i * (0 - min_val) / k, 2) for i in range(k+1)]
    le0['group'] = pd.cut(le0[column], bins_le)

    for i, (group, subset) in enumerate(le0.groupby('group')):
        idx = len(bins_le) - 2 - i  # reverse index for negative values
        if not subset.empty:
            subset.plot(ax=ax, color=color_le, edgecolor='lightgray',
                        markersize=s_conficient * size_coefficient[idx], alpha=1, lw=0.5)
        ax.scatter([], [], c=color_le, s=s_conficient * size_coefficient[idx],
                   label=f'{group.left:.2f} - {group.right:.2f}', ec="lightgray", alpha=0.8, lw=0.5)

    ax.set_xlim(*ax_extent[0])
    ax.set_ylim(*ax_extent[1])
    ax.text(label_pos[0], label_pos[1], 'SAMIs', fontsize=13)
    ax.text(label_pos[0] + 1.5, label_pos[1] + 19, region_name, fontsize=20)
    ax.legend(frameon=False, loc="lower left", fontsize=8, ncol=1, labelspacing=1)

    # Format coordinates
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{abs(x):.0f}°{'E' if x >= 0 else 'W'}"))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: f"{abs(y):.0f}°{'N' if y >= 0 else 'S'}"))
    ax.xaxis.set_major_locator(MultipleLocator(20))
    ax.yaxis.set_major_locator(MultipleLocator(10))

    fig.patch.set_alpha(0.0)
    return fig
