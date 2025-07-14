import pandas as pd
import geopandas as gpd

# Loop through each year (e.g., 2015 to 2022)
for year in range(15, 23):

    print('20', year, "'s intersect started.")

    # Read the input layer (e.g., roads layer)
    input_layer = gpd.read_file(f"/your_path/to/road_data/osm-road-20{year}.shp")

    # Read the overlay layer (e.g., administrative boundaries like cities)
    overlay_layer = gpd.read_file(f"/your_path/to/admin_boundary/20{year}-cities.shp")

    # Ensure both layers use the same coordinate reference system (CRS)
    input_layer = input_layer.to_crs("EPSG:4326")

    # Read city names or region names from an external Excel file
    data = pd.read_excel("/your_path/to/data.xlsx")
    names = data['city']  # Column containing region names

    # Loop through each region name to perform clipping
    for name in names:
        # Use regular expression to filter overlay polygons matching the name
        pattern = f'^{name}'
        filter_condition = overlay_layer['region_name'].str.contains(pattern, regex=True, na=False)
        filtered_overlay = overlay_layer[filter_condition]

        # Convert filtered overlay layer to the same CRS
        filtered_overlay = filtered_overlay.to_crs("EPSG:4326")

        # Perform spatial intersection (clip input layer by overlay)
        intersect_result = gpd.overlay(input_layer, filtered_overlay, how='intersection', keep_geom_type=False)

        # Save the clipped result to CSV
        intersect_result.to_csv(f"/your_output_path/20{year}/road/{name}_osm_road.csv", index=False)

        print(f"{name}'s intersection result has saved.")
