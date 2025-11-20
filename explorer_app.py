import streamlit as st

# streamlit app layout - applied to all pages
st.set_page_config(layout='wide')
st.sidebar.title('About')
st.sidebar.write('Light Pollution x Air Pollution')
st.sidebar.info(
  'This app allows users to explore light pollution and air pollution data'
)
st.sidebar.image("assets/globe_vir_2016_lrg.png")

# pages and navigation
about_page = st.Page('about.py', title='About', icon='ℹ️')
background_page = st.Page('background.py', title='Background', icon='🌃')
explorer_page = st.Page('explorer.py', title='Explore on a map', icon='🧭')

pg = st.navigation([about_page, background_page, explorer_page, ])
pg.run()
