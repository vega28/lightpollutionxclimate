import streamlit as st

st.header('Light Pollution x Air Pollution')
st.subheader('About this project')
# TODO: add project description
st.write('Terra.do Software x Climate Course Final Project - Fall 2025')

st.markdown("""
This project attempts to quantify and visualize the potential relationship between   
artificial light intensity and nighttime air quality across select cities by looking   
at global light pollution and air quality data from google APIs.  
            
The project explores how urban areas are impacted by unshielded light interacting  
with atmospheric gases and how this light pollution and air quality may correlate.
""")



st.subheader('Authors')
# TODO: add author info (if everyone is comfortable with it!)
st.markdown("""
- Misha Craddock - [LinkedIn](https://www.linkedin.com/in/misha-craddock/) - [Github](https://github.com/misha-c)
- Kelsi Flatland - [LinkedIn](https://www.linkedin.com/in/flatland/) - [Github](https://github.com/vega28)
- Nico Leffel - [LinkedIn](https://www.linkedin.com/in/nicoleffel/) - [Github](https://github.com/leffel)
- Rhona Nyakulama - [LinkedIn](https://www.linkedin.com/in/rhona-nyakulama-2b486a25a/)
""")


col1, col2 = st.columns(2)

with col1:
  st.image('assets/nighttime_kigali.png', caption='Nighttime light pollution over Kigali, Rwanda (summer 2024)', use_column_width=True)
  st.image('assets/nighttime_nyc.png', caption='Nighttime light pollution over New York City, US (summer 2024)', use_column_width=True)
with col2:
  st.image('assets/nighttime_sf.png', caption='Nighttime light pollution over San Francisco, US (summer 2024)', use_column_width=True)
  st.image('assets/nighttime_seattle.png', caption='Nighttime light pollution over Seattle, US (summer 2024)', use_column_width=True)