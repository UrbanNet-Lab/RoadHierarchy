import os
import rtree
import openpyxl
import pandas as pd
from shapely import wkt
from geopy.distance import geodesic
from shapely.geometry import LineString, Point

# Extract coordinates from LINESTRING
def extract_coordinates(geometry_str):
    try:
        coordinates_str = geometry_str.replace('LINESTRING (', '').replace(')', '')
        coordinates_list = [coord.split() for coord in coordinates_str.split(', ')]
        return [(float(lon), float(lat)) for lon, lat in coordinates_list]
    except:
        print("Error extracting coordinates:", geometry_str)
        return []

# Extract coordinates from MULTILINESTRING
def extract_multilinestring_coordinates(multilinestring_str):
    multilinestring_str = multilinestring_str.replace('MULTILINESTRING (', '')[:-1]
    linestrings = multilinestring_str.split('), ')
    coords_list = []
    for linestring in linestrings:
        coordinates_str = linestring.replace('(', '').replace(')', '')
        coordinates_list = [coord.split() for coord in coordinates_str.split(', ')]
        coords = [(float(lon), float(lat)) for lon, lat in coordinates_list]
        coords_list.append(coords)
    return coords_list

# Determine whether two LineStrings represent opposite directions of the same road
def is_same_direction(geometry1, geometry2):
    centroid1 = geometry1.centroid
    centroid2 = geometry2.centroid
    zhixin_distance = centroid1.distance(centroid2)
    min_distance = geometry1.distance(geometry2)

    start1, end1 = geometry1.coords[0], geometry1.coords[-1]
    vector1 = Point(end1[0] - start1[0], end1[1] - start1[1])
    start2, end2 = geometry2.coords[0], geometry2.coords[-1]
    vector2 = Point(end2[0] - start2[0], end2[1] - start2[1])

    dot_product = vector1.x * vector2.x + vector1.y * vector2.y
    magnitude1 = (vector1.x ** 2 + vector1.y ** 2) ** 0.5
    magnitude2 = (vector2.x ** 2 + vector2.y ** 2) ** 0.5
    cos_theta = dot_product / (magnitude1 * magnitude2) if magnitude1 * magnitude2 != 0 else 0

    return (
        zhixin_distance < 0.001 and
        1 - abs(cos_theta) < 0.01 and
        cos_theta < 0 and
        0 < min_distance < 0.0003,
        zhixin_distance, min_distance, cos_theta
    )

# Core function to compute total road length for a given class
def compute(road_type, file_path):
    df = pd.read_csv(file_path, low_memory=False)
    roads = df[df['fclass'].isin([road_type, f"{road_type}_link"])]
    roads = roads[~roads['geometry'].str.contains('POINT', na=False)]
    roads_line = roads[~roads['geometry'].str.contains('MULTILINESTRING', na=False)].copy()
    roads_mult = roads[roads['geometry'].str.contains('MULTILINESTRING', na=False)].copy()

    offset = 0.001
    index_rtree = rtree.index.Index()
    geometries = []

    for idx, row in roads_line.iterrows():
        geometry = wkt.loads(row['geometry'])
        geometries.append(geometry)
        centroid = geometry.centroid
        x, y = centroid.x, centroid.y
        bounds = (x - offset/2, y - offset/2, x + offset/2, y + offset/2)
        index_rtree.insert(idx, bounds)

    unique_roads_line = set()
    for index1, row1 in roads_line.iterrows():
        geometry1 = wkt.loads(row1['geometry'])
        centroid1 = geometry1.centroid
        bounds1 = (
            centroid1.x - offset/2, centroid1.y - offset/2,
            centroid1.x + offset/2, centroid1.y + offset/2
        )
        unique_roads_line.add(geometry1)
        possible_matches = list(index_rtree.intersection(bounds1))
        for index2 in possible_matches:
            if index2 == index1:
                continue
            geometry2 = wkt.loads(roads.loc[index2]['geometry'])
            is_dup, _, _, _ = is_same_direction(geometry1, geometry2)
            if is_dup:
                if geometry1.length > geometry2.length:
                    unique_roads_line.discard(geometry2)
                    unique_roads_line.add(geometry1)
                else:
                    unique_roads_line.discard(geometry1)
                    unique_roads_line.add(geometry2)
            else:
                unique_roads_line.add(geometry2)

    line_sum = 0
    for line in unique_roads_line:
        total = sum(
            geodesic((p1[1], p1[0]), (p2[1], p2[0])).km
            for p1, p2 in zip(line.coords[:-1], line.coords[1:])
        )
        line_sum += total

    multline_sum = 0
    if len(roads_mult):
        roads_mult['coordinates'] = roads_mult['geometry'].apply(extract_multilinestring_coordinates)
        for coord_group in roads_mult['coordinates']:
            for line_coords in coord_group:
                multline_sum += sum(
                    geodesic((p1[1], p1[0]), (p2[1], p2[0])).km
                    for p1, p2 in zip(line_coords[:-1], line_coords[1:])
                )

    return line_sum + multline_sum

# Main function
def main():
    # Configuration: update these paths to your environment
    base_input_dir = "/your_output_path/20{year}/road/{name}_osm_road.csv"
    base_output_dir = "/your_path/to/output"
    city_list_path = "/your_path/to/city_list.xlsx"

    city_df = pd.read_excel(city_list_path)
    city_names = city_df['city']

    for year in range(15, 23):
        print(f"Processing year: 20{year}")

        road_types = [
            'motorway', 'primary', 'secondary', 'tertiary', 'trunk',
            'residential', 'service', 'footway', 'subway', 'light_rail', 'monorail'
        ]

        results = []
        for city in city_names:
            city_clean = city.replace("'", "")
            file_path = os.path.join(base_input_dir, f"20{year}/road/{city_clean}_osm_road.csv")

            if not os.path.exists(file_path):
                print(f"File not found: {file_path}")
                continue

            lengths = [compute(rt, file_path) for rt in road_types]
            results.append([city_clean] + lengths)

            print(f"{city_clean} done for year 20{year}: {lengths}")

        # Save results to Excel
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(['City'] + [t.title().replace('_', ' ') for t in road_types])
        for row in results:
            ws.append(row)
        output_path = os.path.join(base_output_dir, f"20{year}_road_lengths.xlsx")
        wb.save(output_path)
        print(f"Year 20{year} result saved to {output_path}")

if __name__ == "__main__":
    main()
