This dataset is used in the script 1_clip_osm_by_city.py, which clips raw OpenStreetMap (OSM) road network data based on the spatial boundaries of each city.

After running the script, the output will contain clipped road network data for each city. These processed results can be directly utilized as inputs for other Python scripts in the project, such as spatial analysis, topological computation, or statistical modeling.

Key Notes:

Input: Raw OSM data and city boundary shapefiles.

Output: Per-city road network shapefiles clipped to city boundaries.

Usage: This preprocessed data enables faster and cleaner downstream operations in the pipeline.

Please ensure that the input data follows the correct coordinate reference system and file structure as expected by 1_clip_osm_by_city.py.
