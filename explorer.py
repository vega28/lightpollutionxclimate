# standard library imports
from datetime import datetime, timedelta
import requests, json, pytz
# 3rd party imports
import ee
import geemap.foliumap as geemap
import streamlit as st
import pandas as pd
from timezonefinder import TimezoneFinder

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
     index=1 # Kigali blows up in Google Air Quality API, choose somewhere else :(
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
m.add_layer(nighttime, nighttime_vis_params, name='Nighttime')
m.add_layer(styled_roi, name='ROI')

m.to_streamlit(height=500)


### pollutant concentration from Google Air Quality API
timeframe = 25
# nico: imo we should only ask for one set of coordinates and store it in state
# so that it gets updated any time they make changes. saves us and our users 
# some sanity. for now, dodging statefulness.
LAT = st.number_input('Lat', value=40.746)
LNG = st.number_input('Lng', value=-73.985)

def fetch_air_quality_data_from_google():
    token = st.secrets['GOOGLE_AQ_TOKEN']
    # fetching air quality data
    url = f'https://airquality.googleapis.com/v1/history:lookup?key={token}'
    data = {
        "location": {
            "latitude": LAT,
            "longitude": LNG
        },
        "hours": timeframe,
        "extraComputations": [
            "POLLUTANT_CONCENTRATION",
        ],
    }
    print(f"data: {data}")
    response = requests.post(url, json=data)
    response_data = response.json()
    return response_data, True if 'error' in response_data else False

def build_pollutant_dataframe(response_data):
    # get no2 and o3 dataframe
    tf = TimezoneFinder()
    tz_name = tf.timezone_at(lat=LAT, lng=LNG)
    local_tz = pytz.timezone(tz_name)

    def _get_data_for_hour(hour):
        utc_time = datetime.fromisoformat(hour['dateTime'])
        formatted_local_time = utc_time.astimezone(local_tz).strftime("%I:%M%p %b %m %Y")
        data = { 'local time': formatted_local_time }
        for pollutant in hour['pollutants']:
            code = pollutant['code'] # the pollutant, ie. 'no2' is nitrogen dioxidem 'o3' is ozone
            if not code in ['no2', 'o3']: continue # we will only look at no2 and o3
            data[code] = pollutant['concentration']['value'] # the concentration of that pollutant at time of measurement
        return data

    no2_and_o3_data = []
    for hour in response_data['hoursInfo']:
        # apparently google sometimes gives null readings, these could be interesting but let's skip them for now
        if not 'pollutants' in hour: continue
        no2_and_o3_data.append(_get_data_for_hour(hour))

    return pd.DataFrame(no2_and_o3_data)

def create_chart_of_pollutants_or_error():
    response_data, error = fetch_air_quality_data_from_google()
    with no2_and_o3_chart:
        if error:
            error_message = f"""
            ## Uh oh! We weren't able to retrieve air quality data.
            
            Error: {response_data['error']['message']}
            """
            st.markdown(error_message)
        else:
            no2_and_o3_df = build_pollutant_dataframe(response_data)
            st.write("NO2 and O3 over the last day")
            st.line_chart(
                no2_and_o3_df, 
                x="local time", 
                y=["no2", "o3"],
                x_label="local time",
                y_label="concentrations in PPB",
            )

no2_and_o3_chart = st.container()

st.button("Make chart", type="secondary", on_click=create_chart_of_pollutants_or_error)