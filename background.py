import streamlit as st

# references helpers
def cite(source_id):
    s = sources[source_id]['ref']
    return f"<sup>[[{s}]](#ref-{s})</sup>"

sources = {
    '11-yr-greece': {
        'ref': 1,
        'title': "Analysis of The 11-Year Record (1987-1997) of Air Pollution Measurements in Athens, Greece. Part II: Photochemical Air Pollutants",
        'link': 'https://www.researchgate.net/profile/P-Kalabokas/publication/348760458_ANALYSIS_OF_THE_11-YEAR_RECORD_1987-1997_OF_AIR_POLLUTION_MEASUREMENTS_IN_ATHENS_GREECE_PART_II_PHOTOCHEMICAL_AIR_POLLUTANTS/links/600fe71545851553a06ff3e1/ANALYSIS-OF-THE-11-YEAR-RECORD-1987-1997-OF-AIR-POLLUTION-MEASUREMENTS-IN-ATHENS-GREECE-PART-II-PHOTOCHEMICAL-AIR-POLLUTANTS.pdf',
    },
    'darksky': {
        'ref': 2,
        'title': 'DarkSky International',
        'link': 'https://darksky.org/',
    },
    'light-vs-wildlife': {
        'ref': 3,
        'title': "How Light Pollution Impacts Wildlife & How You Can Help",
        'link': 'https://www.nwf.org/Magazines/National-Wildlife/2023/Summer/Conservation/Light-Pollution-Wildlife',
    },
    'reaction-diagram': {
        'ref': 4,
        'title': 'Nitrate radicals and biogenic volatile organic compounds: oxidation, mechanisms, and organic aerosol',
        'link': 'https://pmc.ncbi.nlm.nih.gov/articles/PMC6104845/',
    },
    'reaction-diagram-2': {
        'ref': 5,
        'title': 'ECG Atmospheric chemistry at night',
        'link': 'https://www.rsc.org/images/environmental-brief-no-3-2014_tcm18-237724.pdf',
    },
    'ground-O3-NO2' : { 
        'ref': 6,
        'title': "Drivers of nocturnal interactions between ground-level ozone and nitrogen dioxide", 
        'link': 'https://journal.gnest.org/sites/default/files/Submissions/gnest_04843/gnest_04843_published.pdf',
      },
}

data_sources = {
    'viirs': {
        'name': 'VIIRS Stray Light Corrected Nighttime Day/Night Band Composites Version 1',
        'id': 'NOAA/VIIRS/DNB/MONTHLY_V1/VCMSLCFG',
        'link': 'https://developers.google.com/earth-engine/datasets/catalog/NOAA_VIIRS_DNB_MONTHLY_V1_VCMSLCFG',
        'description': '  - temporal coverage: 2014-01-01 - 2025-03-01' 
        # TODO - spatial resolution: ____
    },
    'air-quality': {
        'name': 'Google Air Quality API',
        'id': 'Air Quality - Pollutants Information',
        'link': 'https://developers.google.com/maps/documentation/air-quality',
        'description': '  - temporal coverage: real-time and past 30 days\n  - location coverage: limited'
        # TODO - spatial resolution: ____
    }
    # 'no2': {
    #     'name': 'Sentinel-5P OFFL NO2: Offline Nitrogen Dioxide',
    #     'id': 'COPERNICUS/S5P/OFFL/L3_NO2',
    #     'link': 'https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S5P_OFFL_L3_NO2',
    #     'description': '  - temporal coverage: 2018-06-28 - 2025-10-21\n  - spatial resolution: ____' # TODO
    # },
}


# page content
st.header('Is Light Pollution Negatively Impacting Nighttime Air Quality?', divider=True)
st.image("assets/earth_vir_2016_m.png")
st.subheader('Global Air Quality')
st.markdown(f"""
Air quality is a critical measure of the atmosphere's purity, determined by the concentration of gaseous and particulate pollutants, with poor air quality being a major global health and environmental risk.

Air pollution is primarily caused by anthropogenic sources  such as agricultural practices and burning of fossil fuels for energy and transport, which release precursor compounds like nitrogen oxides that undergo chemical transformations in the atmosphere.{cite('11-yr-greece')}

Key atmospheric gases that significantly impact air quality include ground-level ozone (O₃) and nitrogen dioxide (NO₂).
""", unsafe_allow_html=True)

st.subheader('Global Light Pollution')
st.markdown(f"""
Light pollution is excessive human-made light at night that disrupts natural darkness.

Light pollution has a myriad of well studied, extremely negative impacts on all life on the planet. Including but not limited to: 
- Wildlife: Disrupts migrations (yearly and daily), nighttime foraging patterns, and reproductive habits, exacerbates habitat degradation and increases mortality rates  
- Human Health: Interferes with natural circadian cycles and is linked to several medical conditions, including depression/mental health, hormone disorders, cancers, and cardiovascular disease to name a few… ~80% of people live under polluted skies 
- Climate: “DarkSky.Org{cite('darksky')} estimates that least 30 percent of all outdoor lighting in the U.S. alone is wasted, mostly by lights that aren’t shielded. That adds up to $3.3 billion and the release of 21 million tons of carbon dioxide per year!”{cite('light-vs-wildlife')}
""", unsafe_allow_html=True)

st.subheader('Possible Interaction?')
st.markdown("""
During nighttime O₃ is usually depleted through a natural 'cleansing' reaction involving the nitrate radical (NO₃), but light pollution from urban areas can disrupt this process by causing a photochemical reaction and destroying the NO₃ radical, thereby keeping pollutant concentrations higher overnight and potentially increasing  O₃ levels for the following day.

The key player here is the nitrate radical (NO₃) that forms at night when ozone reacts with nitrogen dioxide:

NO₂ + O₃ → NO₃ + O₂

The nitrate radical is highly reactive and only exists significantly at night because sunlight rapidly breaks it down during the day (photolysis). At night, it becomes a major oxidant in the atmosphere.

New studies show that photolysis is occurring at night as well due to artificial light interacting with  nitrate radicals.
""", unsafe_allow_html=True)

st.image("assets/no3-chem.jpg")
st.markdown(f"""
Diagram of nitrate radicals interaction{cite('reaction-diagram')}{cite('reaction-diagram-2')}
""", unsafe_allow_html=True)
st.image("assets/interaction-graphic.png")
st.markdown(f"""
This confirms that light pollution can reach levels that might affect nocturnal  O₃ and NO₂ concentrations; therefore, monitoring the impact of light pollution is essential for air pollution assessment.{cite('ground-O3-NO2')}

Using Google Air Quality data sets Central Park (NYC), and pulling hourly data for current time up to 48 hours in the past, which gives a couple day and night periods, we plotted data from the 17th - 19th November 2025 and the chart below refers:
""", unsafe_allow_html=True)

st.image("assets/nyc-chart.png")
st.markdown("""
Nitrogen dioxide interacts with ozone to produce a nitrate radical (NO₃) that helps to clean out ozone particles at night.  The chart models a similar path where we observe high content on ozone particles during the dark/night time, especially between 17h and midnight. This could mean that light pollution is affecting the natural ozone cleaning process by destroying the nitrate radical, as explained above.  Furthermore, the concentration of the Nitrogen dioxide and Ozone pollutants in the atmosphere are way above recommended levels.
""", unsafe_allow_html=True)


# references
st.header('Sources', divider=True)

st.subheader('Data Sources')
for source_id in data_sources:
    s = data_sources[source_id]
    st.markdown(f"- {s['name']}: [{s['id']}]({s['link']})\n{s['description']}")

st.subheader('References')
for source_id in sources:
    s = sources[source_id]
    st.html(f"[{s['ref']}] <a id='ref-{s['ref']}' href=\"{s['link']}\">{s['title']}</a>")
