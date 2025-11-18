import streamlit as st

# streamlit app layout - applied to all pages
st.set_page_config(layout='wide')
st.sidebar.title('About')
st.sidebar.write('Light Pollution x Air Pollution')
st.sidebar.info(
  'This app allows users to explore light pollution and air pollution data'
)

# pages and navigation
background_page = st.Page('background.py', title='Background', icon='🌃')
explorer_page = st.Page('explorer.py', title='Explore on a map', icon='🧭')
about_page = st.Page('about.py', title='About', icon='ℹ️')

pg = st.navigation([background_page, explorer_page, about_page])
pg.run()
