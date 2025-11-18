# standard library imports
from datetime import datetime, timedelta
from pprint import pprint
# 3rd party imports
import ee
import geemap.foliumap as geemap
# import pydeck as pdk
import streamlit as st

# access GEE
ee.Authenticate()
ee.Initialize(project='cybernetic-tide-309501')

try:
   confirmation = ee.String('Hello from the Earth Engine servers!').getInfo()
except Exception as e:
   st.write("Error connecting to GEE:", e)

# streamlit app layout
st.set_page_config(layout='wide')
st.title('Light Pollution x Air Pollution Explorer')

st.sidebar.title('About')
st.sidebar.info(
  'This app allows users to explore light pollution and air pollution data'
)

col1, col2 = st.columns(2)

with col1:
  start_date = st.date_input('Choose a start date for a two-month range to investigate', datetime(2024, 6, 1) - timedelta(days=60))
  # top left coordinate
  x_min, y_max = st.number_input('Minimum Longitude', value=-123.005470), st.number_input('Maximum Latitude', value=38.003892)
  # bottom right coordinate
  x_max, y_min = st.number_input('Maximum Longitude', value=-121.588234), st.number_input('Minimum Latitude', value=37.207518)
with col2:
  st.write(f'Your chosen date range is: {start_date} to {start_date + timedelta(days=60)}')
  st.write(f'Your chosen region of interest is defined by the bounding box with upper left coordinate ({y_max},{x_min}) and lower right coordinate ({y_min},{x_max})')

# define helper functions

def get_mosaic(image_collection, date):
    """
    Mosaic is where you take an ImageCollection and flatten it to a single image. 
    It uses the pixels from the "top" images first, then fills in any holes with lower images
    We mosaic together data over a period of time so that we can fill in any holes from cloud cover

    returns: ee.image.Image
    """
    return (
        image_collection
        # Filter to a 2-month date rage so that our mosaic merges together that range of data
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

# convert Date to Datetime
start_date = datetime(start_date.year, start_date.month, start_date.day)

# define ROI polygon as a sequence of points, forming a rectangle
# start in the bottom left, move clockwise through the vertices, and return back to the starting point.
roi_polygon = ee.Geometry.Polygon([
    [x_min, y_min],
    [x_min, y_max],
    [x_max, y_max],
    [x_max, y_min],
    [x_min, y_min],
])
roi_bounds = (x_min, y_min, x_max, y_max)

# VIIRS Stray Light Corrected Nighttime Day/Night Band Composites Version 1
viirs_collection = ee.ImageCollection('NOAA/VIIRS/DNB/MONTHLY_V1/VCMSLCFG').select('avg_rad')#.filterBounds(roi_polygon)
# Sentinel-5P OFFL NO2: Offline Nitrogen Dioxide
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
m.zoom_to_bounds(roi_bounds)
m.add_basemap('OpenTopoMap')
m.add_layer(nighttime, nighttime_vis_params, name='Nighttime')
m.add_layer(tropospheric_no2, no2_vis_params, name='Tropospheric NO2 Column Density')
m.add_layer(styled_roi, name='ROI')

m.to_streamlit(height=500)

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










