# standard library imports
from datetime import datetime, timedelta
# 3rd party imports
import ee
import geemap.foliumap as geemap
import streamlit as st


# authenticate and access GEE
ee.Authenticate()
ee.Initialize(project='cybernetic-tide-309501')

try:
   confirmation = ee.String('Hello from the Earth Engine servers!').getInfo()
except Exception as e:
   st.write("Error connecting to GEE:", e)


# helper functions
def get_mosaic(image_collection, date):
    """
    Mosaic is where you take an ImageCollection and flatten it to a single image. 
    It uses the pixels from the "top" images first, then fills in any holes with lower images
    We mosaic together data over a period of time so that we can fill in any holes from cloud cover

    returns: ee.image.Image
    """
    return (
        image_collection
        # note: filters to a 2-month date rage so that our mosaic merges together that range of data
        .filterDate(date, date + timedelta(days=60))
        .mosaic()
    )

def get_annual(collection, year):
    """ 
    filter a collection by year
    input must be ImageCollection filtered by band 

    returns ee.image.Image
    """
    return collection.filter(ee.Filter.eq("system:index", year))

# constants
max_date = datetime(2025, 3, 1)  # limited by viirs: 2014-01-01 - 2025-03-01
min_date = datetime(2018, 6, 28) # limited by NO2: 2018-06-28 - 2025-10-21
preset_regions = {
    'Kigali': {
        'x_min': 29.992346,
        'y_max': -1.909109,
        'x_max': 30.181946,
        'y_min': -1.990146
    },
    'New York City': {
        'x_min': -74.015999,
        'y_max': 40.731456,
        'x_max': -73.877297,
        'y_min': 40.588735
    },
    'San Francisco Bay Area': {
        'x_min': -123.005470,
        'y_max': 38.003892,
        'x_max': -121.588234,
        'y_min': 37.207518
    },
    'Seattle': {
        'x_min': -122.448617,
        'y_max': 47.739050,
        'x_max': -122.085439,
        'y_min': 47.433840
    }
}


# user inputs
col1, col2 = st.columns(2)
# TODO: 
# - make this pretty
# - add preset dates?
# - adjust functionality for custom coordinates to be less laggy?
with col1:
  start_date = st.date_input(
     'Choose a start date for a two-month range to investigate', 
     datetime(2024, 6, 1) - timedelta(days=60),
     min_value = min_date,
     max_value = max_date - timedelta(days=60)
     )
  preset_region_choice = st.selectbox(
     'Choose a preset region or enter custom coordinates below', 
     list(preset_regions.keys()) + ['Custom'], 
     index=0
     )
  if preset_region_choice != 'Custom':
    region = preset_regions[preset_region_choice]
    x_min = region['x_min']
    y_max = region['y_max']
    x_max = region['x_max']
    y_min = region['y_min']  
  else:
    # top left coordinate
    x_min = st.number_input('Minimum Longitude', value=0)
    y_max = st.number_input('Maximum Latitude', value=1)
    # bottom right coordinate
    x_max = st.number_input('Maximum Longitude', value=1)
    y_min = st.number_input('Minimum Latitude', value=0)

with col2:
  st.write(f'Your chosen date range is: {start_date} to {start_date + timedelta(days=60)}')
  st.write(f'Your chosen region of interest is defined by the bounding box with upper left coordinate ({y_max},{x_min}) and lower right coordinate ({y_min},{x_max})')


# reformat input data
start_date = datetime(start_date.year, start_date.month, start_date.day)
roi_polygon = ee.Geometry.Polygon([
    [x_min, y_min],
    [x_min, y_max],
    [x_max, y_max],
    [x_max, y_min],
    [x_min, y_min],
])
roi_bounds = (x_min, y_min, x_max, y_max)

# fetch data
viirs_collection = ee.ImageCollection('NOAA/VIIRS/DNB/MONTHLY_V1/VCMSLCFG').select('avg_rad')#.filterBounds(roi_polygon)
no2_collection = ee.ImageCollection('COPERNICUS/S5P/OFFL/L3_NO2').select('tropospheric_NO2_column_number_density')#.filterBounds(roi_polygon)

# aggregate data
nighttime = get_mosaic(viirs_collection, start_date) 
tropospheric_no2 = get_mosaic(no2_collection, start_date)

# define visual parameters
styled_roi = ee.FeatureCollection(ee.Feature(roi_polygon)).style(color='FFFFFFFF', fillColor='00000000')
nighttime_vis_params = { 'min': 0.0, 'max': 60.0 } # avg radiance values can go higher but that is excessive... Vegas will just be saturated
no2_vis_params = {
  'min': 0,
  'max': 0.0002,
  'palette': ['black', 'blue', 'purple', 'cyan', 'green', 'yellow', 'red']
}

# create an interactive map
m = geemap.Map()
# TODO: 
# - add legend
# - add something to indicate pixel size
m.zoom_to_bounds(roi_bounds)
m.add_basemap('OpenTopoMap')
m.add_layer(tropospheric_no2, no2_vis_params, name='Tropospheric NO2 Column Density')
m.add_layer(nighttime, nighttime_vis_params, name='Nighttime')
m.add_layer(styled_roi, name='ROI')

m.to_streamlit(height=500)


# TODO: fix the following map or remove it!
st.header('Explore Annual Data')

# Create a layout containing two columns, one for the map and one for the layer dropdown list.
row1_col1, row1_col2 = st.columns([3, 1])

# Valid epochs for both datasets range from 2018 to 2024.
years = ["2019", "2020", "2021", "2022", "2023", "2024"]

# Add a dropdown list and checkbox to the second column.
with row1_col2:
    selected_year = st.selectbox("Select a year", years)
    # add_legend = st.checkbox("Show legend")

with row1_col1:    
    m2 = geemap.Map()
    m2.zoom_to_bounds(roi_bounds)
    m2.add_basemap('OpenTopoMap')
    # FIXME: trouble getting these layers...
    m2.add_layer(get_annual(viirs_collection, selected_year), nighttime_vis_params, name='Nighttime')
    m2.add_layer(get_annual(no2_collection, selected_year), no2_vis_params, name='Tropospheric NO2 Column Density')
    m2.add_layer(styled_roi, name='ROI')
    m2.to_streamlit(height=500)
