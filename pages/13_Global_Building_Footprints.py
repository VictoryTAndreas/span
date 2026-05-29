import ee
import geemap.foliumap as geemap
import geopandas as gpd
import streamlit as st
import json

service_account = st.secrets["earthengine"]["json"]
credentials = ee.ServiceAccountCredentials(
    json.loads(service_account)["client_email"],
    key_data=service_account
)
ee.Initialize(credentials)

st.set_page_config(layout="wide")

st.sidebar.info(
    """
    - Developed By: <https://www.vtanamibia.com>
    - Contact us for similar projects: <https://www.vtanamibia.com>
    """
)

st.sidebar.title("Contact")
st.sidebar.info(
    """
    VTA Namibia at [vtanamibia.com](https://www.vtanamibia.com) | 
    [GitHub](https://github.com/VictoryTAndreas) | 
    [Twitter](https://twitter.com/vicanddotvta) | 
    [YouTube](https://youtube.com/@vtastudios) | 
    [LinkedIn](https://www.linkedin.com/company/vta-labs-studios/?originalSubdomain=na)
    """
)

st.title("Global Building Footprints")

col1, col2 = st.columns([8, 2])


@st.cache_data
def read_data(url):
    return gpd.read_file(url)


countries = "https://github.com/giswqs/geemap/raw/master/examples/data/countries.geojson"
states = "https://github.com/giswqs/geemap/raw/master/examples/data/us_states.json"

countries_gdf = read_data(countries)
states_gdf = read_data(states)

country_names = countries_gdf["NAME"].values.tolist()
country_names.remove("United States of America")
country_names.append("USA")
country_names.sort()
country_names = [name.replace(".", "").replace(" ", "_") for name in country_names]

state_names = states_gdf["name"].values.tolist()

basemaps = list(geemap.basemaps)

Map = geemap.Map()

with col2:

    basemap = st.selectbox("Select a basemap", basemaps, index=basemaps.index("HYBRID"))
    Map.add_basemap(basemap)

    country = st.selectbox(
        "Select a country", country_names, index=country_names.index("USA")
    )

    fc = None  # guard against undefined reference below

    if country == "USA":
        state = st.selectbox(
            "Select a state", state_names, index=state_names.index("Florida")
        )
        layer_name = state
        try:
            fc = ee.FeatureCollection(
                f"projects/sat-io/open-datasets/MSBuildings/US/{state}"
            )
        except Exception as e:
            st.error(f"No data available for the selected state: {e}")
            st.stop()
    else:
        layer_name = country
        try:
            fc = ee.FeatureCollection(
                f"projects/sat-io/open-datasets/MSBuildings/{country}"
            )
        except Exception as e:
            st.error(f"No data available for the selected country: {e}")
            st.stop()

    color = st.color_picker("Select a color", "#FF5500")
    style = {"fillColor": "00000000", "color": color}

    split = st.checkbox("Split-panel map")

    if split:
        left = geemap.ee_tile_layer(fc.style(**style), {}, "Left")
        right = left
        Map.split_map(left, right)
    else:
        Map.addLayer(fc.style(**style), {}, layer_name)

    Map.centerObject(fc.first(), zoom=16)

    with st.expander("Data Sources"):
        st.info(
            """
            [Microsoft Building Footprints](https://gee-community-catalog.org/projects/msbuildings/)
            """
        )

with col1:
    Map.to_streamlit(height=1000)