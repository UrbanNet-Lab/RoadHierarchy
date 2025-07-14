import numpy as np
import seaborn as sns
import pandas as pd
from shapely.geometry import LineString, Point, MultiLineString
from shapely import wkt
import matplotlib.pyplot as plt

def process_geometry(location_type_dict, geom, row_type):
    """
    Parse the geometry string into shapely object and
    map coordinates to road types in a dictionary.
    """
    geom = wkt.loads(geom)
    try:
        if isinstance(geom, LineString):
            for coord in geom.coords:
                coord_str = str(coord)
                if coord_str not in location_type_dict:
                    location_type_dict[coord_str] = {row_type}
                else:
                    location_type_dict[coord_str].add(row_type)

        elif isinstance(geom, Point):
            point_str = str(geom)
            if point_str not in location_type_dict:
                location_type_dict[point_str] = {row_type}
            else:
                location_type_dict[point_str].add(row_type)

        elif isinstance(geom, MultiLineString):
            for line in geom.geoms:
                for coord in line.coords:
                    coord_str = str(coord)
                    if coord_str not in location_type_dict:
                        location_type_dict[coord_str] = {row_type}
                    else:
                        location_type_dict[coord_str].add(row_type)

    except Exception as e:
        print(f"Error processing geometry: {e}")

def merge_matrix(matrix, road_types):
    """
    Merge specific columns and rows of the connection matrix
    and remove corresponding road types to simplify the matrix.
    """
    for i in range(len(matrix)):
        matrix[i][0] += matrix[i][1]  # Merge column 2 into column 1
        matrix[i][5] += matrix[i][6]  # Merge column 7 into column 6
        del matrix[i][6]  # Remove column 7
        del matrix[i][1]  # Remove column 2

    for i in range(len(matrix[0])):
        matrix[0][i] += matrix[1][i]  # Merge row 2 into row 1
        matrix[5][i] += matrix[6][i]  # Merge row 7 into row 6

    del matrix[6]  # Remove row 7
    del matrix[1]  # Remove row 2

    matrix[0][0] = 0
    matrix[4][4] = 0

    del road_types[6]  # Remove road type at index 6
    del road_types[1]  # Remove road type at index 1

    return matrix, road_types

def process_match(df, road_types):
    """
    Build a connection matrix of road types based on shared coordinates.
    """
    location_type_dict = {}

    # Map all geometry points to their road types
    for _, row in df.iterrows():
        geom = row['geometry']
        row_type = row['fclass']
        process_geometry(location_type_dict, geom, row_type)

    # Initialize connection matrix with zeros
    matrix = [[0] * len(road_types) for _ in range(len(road_types))]

    # Count occurrences of each road type
    counts = {road_type: 0 for road_type in road_types}

    # Build symmetric matrix of co-occurrence counts
    for types_set in location_type_dict.values():
        # Count each road type occurrence
        for t in types_set:
            if t in road_types:
                counts[t] += 1

        # Update matrix for points belonging to multiple road types
        if len(types_set) > 1:
            types_list = list(types_set)
            for i, type1 in enumerate(types_list):
                if type1 not in road_types:
                    continue
                for j in range(i, len(types_list)):
                    type2 = types_list[j]
                    if type2 not in road_types or type1 == type2:
                        continue
                    idx1 = road_types.index(type1)
                    idx2 = road_types.index(type2)
                    matrix[idx1][idx2] += 1
                    matrix[idx2][idx1] += 1  # Keep symmetric

    # Merge specified rows and columns to simplify matrix
    matrix, road_types = merge_matrix(matrix, road_types)

    # Normalize matrix rows by row sums to get connection ratios
    row_sums = [sum(row) for row in matrix]
    for i in range(len(road_types)):
        for j in range(len(road_types)):
            matrix[i][j] = matrix[i][j] / row_sums[i] if row_sums[i] != 0 else 0

    return matrix

def plot_draw_heatmap(matrix, road_types):
    """
    Plot a heatmap of the connection matrix between road types.
    """
    road_types_cap = [s.capitalize() if s else '' for s in road_types]
    plt.figure(figsize=(10, 7))
    sns.heatmap(matrix, annot=False, cmap="viridis",
                cbar_kws={'label': 'Connection Correlation',
                          'ticks': np.arange(0, 0.9, 0.1)},
                vmin=0, vmax=0.8)
    ax = plt.gca()
    ax.set_xticklabels(road_types_cap, fontsize=13)
    ax.set_yticklabels(road_types_cap, fontsize=13)
    ax.set_aspect('equal', adjustable='box')
    plt.savefig('road_connection_heatmap.pdf', dpi=300)
    plt.show()

def main():
    """
    Main execution function.
    Replace file paths and filenames with your own data.
    """
    # Example placeholders for file paths and filenames
    excel_path = 'path_to_city_label_excel.xlsx'
    city_roads_csv_dir = 'path_to_city_road_csv_files/'

    # Load city names and labels
    data = pd.read_excel(excel_path)
    city_names = data[['city', 'label']]

    road_types = ['motorway', 'trunk', 'primary', 'secondary', 'tertiary', 'residential', 'service', 'footway']
    matrices = []

    # Process each city file
    for row in city_names.values:
        city_name = row[0]
        # Construct CSV path for the city (replace with actual path logic)
        city_csv_path = f'{city_roads_csv_dir}{city_name}_osm_road.csv'
        df = pd.read_csv(city_csv_path, low_memory=False)

        matrix = process_match(df, road_types.copy())
        matrices.append(matrix)

    # Compute mean connection matrix over all cities
    mean_matrix = np.mean(matrices, axis=0)

    # Plot heatmap for a subset of road types after merging
    reduced_road_types = ['motorway', 'primary', 'secondary', 'tertiary', 'residential', 'footway']
    plot_draw_heatmap(mean_matrix, reduced_road_types)

if __name__ == '__main__':
    main()
