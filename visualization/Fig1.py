"""
Visualize the spatial distribution of cities in China and the USA.
Generates a two-panel figure showing city-level population and location.
"""

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point
from matplotlib.ticker import FuncFormatter, MultipleLocator

# Set font for plotting
plt.rcParams['font.family'] = ['Arial']
plt.rcParams['axes.unicode_minus'] = False

# ----- Utility Functions -----

def dms_to_dd(dms):
    """Convert DMS (degrees, minutes, seconds) format to decimal degrees."""
    try:
        dms = dms.replace('°', ' ').replace('′', ' ').replace("''", ' ').strip()
        is_negative = 'S' in dms or 'W' in dms
        dms = dms.replace('N', '').replace('S', '').replace('E', '').replace('W', '')
        parts = dms.split()
        degrees = float(parts[0])
        minutes = float(parts[1]) if len(parts) > 1 else 0
        seconds = float(parts[2]) if len(parts) > 2 else 0
        dd = degrees + minutes / 60 + seconds / 3600
        return -dd if is_negative else dd
    except:
        return None

def format_lon(x, pos): return f"{abs(x):.0f}°{'E' if x >= 0 else 'W'}"
def format_lat(y, pos): return f"{abs(y):.0f}°{'N' if y >= 0 else 'S'}"

# ----- Plotting Functions -----

def plot_china(china_gdf, china_base, ax, nine_line=None):
    """Plot Chinese cities and background."""
    china_base.to_crs(epsg=4326).plot(ax=ax, fc="white", ec="gray", lw=0.6, alpha=0.7)
    colors = {'Municipalities': '#E21C21', 'Prefectural-level': '#3A7CB5', 'County-level': '#51AE4F'}

    for level, color in colors.items():
        subset = china_gdf[china_gdf['rank'] == level]
        size = 12 if level != 'County-level' else 3
        ax.scatter(subset['lon'], subset['lat'], s=subset['normalized_pop']/size, c=color, edgecolor='lightgray', lw=0.5, label=level)

    if nine_line is not None:
        ax_inset = ax.inset_axes([0.7, 0.07, 0.4, 0.3])
        china_base.plot(ax=ax_inset, fc="white", ec="gray", lw=0.6)
        nine_line.plot(ax=ax_inset, color='black')
        ax_inset.set_xticks([]); ax_inset.set_yticks([])

    ax.set_xlim(70, 139); ax.set_ylim(15, 55)
    ax.legend(frameon=False)
    ax.xaxis.set_major_formatter(FuncFormatter(format_lon))
    ax.yaxis.set_major_formatter(FuncFormatter(format_lat))

def plot_usa(usa_gdf, usa_base, ax):
    """Plot US MSAs and μSAs."""
    usa_base.to_crs(epsg=4326).plot(ax=ax, fc="white", ec="gray", lw=0.6, alpha=0.7)
    colors = {'M1': '#3A7CB5', 'M2': '#51AE4F'}

    for label, color in colors.items():
        subset = usa_gdf[usa_gdf['LSAD'] == label]
        factor = 100000 if label == 'M1' else 7600
        ax.scatter(subset['lon'], subset['lat'], s=subset['normalized_pop']/factor, c=color, edgecolor='lightgray', lw=0.5, label=label)

    ax.set_xlim(-128, -66); ax.set_ylim(22, 54)
    ax.legend(frameon=False)
    ax.xaxis.set_major_formatter(FuncFormatter(format_lon))
    ax.yaxis.set_major_formatter(FuncFormatter(format_lat))

# ----- Main Execution -----

def main():
    # Load and preprocess Chinese city data
    # Placeholder: replace with actual file paths
    china_base = gpd.read_file("path/to/china_boundary.shp")
    china_gdf = pd.read_excel("path/to/china_city_data.xlsx")
    nine_line = gpd.read_file("path/to/nine_line.shp")
    china_gdf['lat'] = china_gdf['lat'].astype(str).apply(dms_to_dd)
    china_gdf['lon'] = china_gdf['lon'].astype(str).apply(dms_to_dd)
    china_gdf['geometry'] = [Point(xy) for xy in zip(china_gdf['lon'], china_gdf['lat'])]
    china_gdf = gpd.GeoDataFrame(china_gdf, geometry='geometry', crs='EPSG:4326')
    china_gdf['normalized_pop'] = china_gdf['2022pop']

    # Load and preprocess US city data
    usa_base = gpd.read_file("path/to/usa_boundary.shp")
    usa_gdf = pd.read_excel("path/to/usa_city_data.xlsx")
    usa_gdf['lat'] = usa_gdf['lat'].astype(str).apply(dms_to_dd)
    usa_gdf['lon'] = usa_gdf['lon'].astype(str).apply(dms_to_dd)
    usa_gdf['geometry'] = [Point(xy) for xy in zip(usa_gdf['lon'], usa_gdf['lat'])]
    usa_gdf = gpd.GeoDataFrame(usa_gdf, geometry='geometry', crs='EPSG:4326')
    usa_gdf['normalized_pop'] = usa_gdf['dp1_0001c']

    # Plotting
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.3), dpi=300)
    plot_usa(usa_gdf, usa_base, axes[0])
    axes[0].set_title("USA Cities", fontsize=12)

    plot_china(china_gdf, china_base, axes[1], nine_line=nine_line)
    axes[1].set_title("China Cities", fontsize=12)

    plt.tight_layout()
    plt.savefig("figures/figure1_spatial_distribution.pdf")
    plt.show()

if __name__ == "__main__":
    main()
