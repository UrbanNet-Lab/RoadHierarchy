import numpy as np
import seaborn as sns
import pandas as pd
from shapely.geometry import LineString, Point
from shapely import wkt
import rtree
from geopy.distance import geodesic
import matplotlib.pyplot as plt

def geodesic_length(linestring):
    """Calculate the total geodesic length (in km) of a LineString by summing distances between adjacent points."""
    coords = list(linestring.coords)
    total_length = sum(
        geodesic((coords[i][1], coords[i][0]), (coords[i+1][1], coords[i+1][0])).km
        for i in range(len(coords) - 1)
    )
    return total_length

def are_aligned(geom1, geom2):
    """Determine if two LineStrings are aligned by calculating the angle between their direction vectors."""
    if isinstance(geom1, LineString):
        start1, end1 = geom1.coords[0], geom1.coords[-1]
        vector1 = Point(end1[0] - start1[0], end1[1] - start1[1])
    if isinstance(geom2, LineString):
        start2, end2 = geom2.coords[0], geom2.coords[-1]
        vector2 = Point(end2[0] - start2[0], end2[1] - start2[1])

    dot_product = vector1.x * vector2.x + vector1.y * vector2.y
    magnitude1 = (vector1.x ** 2 + vector1.y ** 2) ** 0.5
    magnitude2 = (vector2.x ** 2 + vector2.y ** 2) ** 0.5

    if magnitude1 * magnitude2 == 0:
        cos_theta = 0
    else:
        cos_theta = dot_product / (magnitude1 * magnitude2)

    # Relaxed condition: aligned if cosine close to 1 or -1 (angle near 0 or 180 degrees)
    return 1 - abs(cos_theta) < 0.1

def process_match(target_road_type, df, road_types, matched_rows):
    """
    Find parallel roads of types other than target_road_type that are aligned and spatially close.
    Uses an R-tree spatial index for efficiency.
    """
    # Create spatial index
    index_rtree = rtree.index.Index()
    offset = 0.001  # Bounding box size for R-tree queries

    # Filter out geometries that are not LineStrings
    df = df[~df['geometry'].str.contains('POINT')]
    df = df[~df['geometry'].str.contains('MULTILINESTRING')].copy()

    # Build R-tree index based on centroids of LineStrings
    for idx, row in df.iterrows():
        try:
            if 'LINESTRING' in row['geometry']:
                geom = wkt.loads(row['geometry'])
                centroid = geom.centroid
                x, y = centroid.x, centroid.y
                bounds = (x - offset/2, y - offset/2, x + offset/2, y + offset/2)
                index_rtree.insert(idx, bounds)
        except Exception as e:
            print(f"Error processing row {idx}: {e}")

    # Filter rows of the target road type only (e.g., 'motorway')
    target_rows = df[df['fclass'].str.contains(f'{target_road_type}')]

    matched_osm_ids = set()

    # For each road of target type, find aligned roads of other types nearby
    for idx1, row1 in target_rows.iterrows():
        if 'LINESTRING' not in row1['geometry']:
            continue
        geom1 = wkt.loads(row1['geometry'])
        type1 = row1['fclass']
        road1 = row1['osm_id']

        # Remove '_link' suffix if present
        if type1.endswith('_link'):
            type1 = type1[:-len('_link')]

        centroid1 = geom1.centroid
        bounds1 = (centroid1.x - offset/2, centroid1.y - offset/2, centroid1.x + offset/2, centroid1.y + offset/2)

        possible_matches = list(index_rtree.intersection(bounds1))
        for idx2 in possible_matches:
            if idx2 == idx1:
                continue
            row2 = df.loc[idx2]
            geom2_str = row2['geometry']
            road2 = row2['osm_id']
            type2 = row2['fclass']

            if type2.endswith('_link'):
                type2 = type2[:-len('_link')]

            # Match only if type2 differs from target and is in road_types
            if type2 != target_road_type and type2 in road_types:
                geom2 = wkt.loads(geom2_str)
                if are_aligned(geom1, geom2):
                    road_pair = tuple(sorted([road1, road2]))
                    if road_pair not in matched_osm_ids:
                        matched_osm_ids.add(road_pair)
                        matched_rows.append({
                            'osm_id': road2,
                            'match_type': target_road_type,
                            'type': type2,
                            'geometry': row2['geometry'],
                        })

    return matched_rows

def main():
    """
    Example main function to demonstrate usage.
    Replace file loading and saving paths with actual ones.
    """
    # Placeholder path to city list with columns including 'city'
    city_list_path = 'path_to_city_list_excel.xlsx'

    # Read city names
    data = pd.read_excel(city_list_path)
    city_names = data[['city']]

    road_types = [
        'subway', 'light_rail', 'monorail', 'motorway', 'trunk', 'primary', 'secondary',
        'tertiary', 'residential', 'service', 'footway'
    ]

    for city_row in city_names.values:
        city = city_row[0]

        # Placeholder paths for road and railway CSVs
        road_csv_path = f'path_to_road_csv/{city}_osm_road.csv'
        rail_csv_path = f'path_to_railway_csv/{city}_osm_railway.csv'

        df_road = pd.read_csv(road_csv_path, low_memory=False)
        df_rail = pd.read_csv(rail_csv_path, low_memory=False)

        df_combined = pd.concat([df_road, df_rail], ignore_index=True)

        all_matches = []

        for c in road_types:
            all_matches = process_match(c, df_combined, road_types, all_matches)

        all_matches_df = pd.DataFrame(all_matches).drop_duplicates(subset=['osm_id', 'type'])

        # If empty, save a default row
        if all_matches_df.empty:
            all_matches_df = pd.DataFrame([{
                'osm_id': 0,
                'match_type': 'none',
                'type': 'none',
                'geometry': 'NONE'
            }])

        # Placeholder output path
        output_path = f'path_to_output/{city}_matrix.csv'
        all_matches_df.to_csv(output_path, index=False, encoding='utf-8')

        print(f"Matches saved for city {city} at {output_path}")

if __name__ == '__main__':
    main()
