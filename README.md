# Urban Road Network Analysis Based on OSM Data

This repository contains the main Python scripts used in my research on urban road networks using OpenStreetMap (OSM) data. The analysis includes clipping city-level OSM data, computing road segment lengths, exploring connectivity patterns among road hierarchies, and detecting parallel road segments.

---

## Project Overview

The goal of this project is to analyze structural properties of urban road networks from OSM data with a focus on:

- Extracting city-specific road data subsets
- Accurately computing geodesic lengths of roads
- Investigating connectivity correlations among different road types
- Identifying spatially parallel or aligned roads to reveal hierarchical relationships

---

## Scripts Description

### 1. `1-clip_osm_by_city.py`  
Clip global or regional OSM data into city-level subsets using city boundary polygons. This step prepares focused datasets for each city to enable efficient downstream analysis.

### 2. `2-compute_osm_road_length.py`  
Calculate geodesic lengths of individual road segments in each city dataset. This script uses geospatial calculations to account for Earth's curvature, ensuring accurate length measurements.

### 3. `3-connecting.py`  
Analyze and quantify the connectivity between different hierarchical road types (e.g., motorway, primary, secondary). The output includes connection correlation matrices, which help in understanding road network structure.

### 4. `4-parallel.py`  
Detect parallel or spatially aligned road segments within city road networks. By combining spatial indexing (R-tree) and geometric alignment checks, this script identifies roads likely to be functionally or hierarchically related.

---

## Requirements

- Python 3.7 or higher
- Required Python packages:
  - numpy
  - pandas
  - shapely
  - rtree
  - geopy
  - matplotlib
  - seaborn

You can install dependencies via pip:

```bash
pip install numpy pandas shapely rtree geopy matplotlib seaborn
