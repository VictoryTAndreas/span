import folium
import pandas as pd
import streamlit as st
import leafmap.foliumap as leafmap
import folium.plugins as plugins

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

st.title("National Library of Scotland XYZ Layers")

df = pd.read_csv("data/scotland_xyz.tsv", sep="\t")
basemaps = leafmap.basemaps
names = df["Name"].values.tolist() + list(basemaps.keys())
links = df["URL"].values.tolist() + list(basemaps.values())

col1, col2, col3, col4, col5, col6 = st.columns([3, 3, 1, 1, 1, 1.5])

with col1:
    left_name = st.selectbox(
        "Select the left layer",
        names,
        index=names.index("Great Britain - Bartholomew Half Inch, 1897-1907"),
    )

with col2:
    right_name = st.selectbox(
        "Select the right layer",
        names,
        index=names.index("HYBRID"),
    )

with col3:
    lat = st.text_input("Latitude", "55.68")

with col4:
    lon = st.text_input("Longitude", "-2.98")

with col5:
    zoom = st.text_input("Zoom", "6")

with col6:
    checkbox = st.checkbox("Add OS 25 inch")

with st.expander("Acknowledgements"):
    st.markdown(
        """
        The map tile access is by kind arrangement of the National Library of Scotland 
        for personal purposes. They host most layers except:
        - Roy Maps — owned by the British Library.
        - GB OS maps 1:25,000 (1937–61) and One Inch 7th series (1955–61) — hosted by MapTiler.

        For website, commercial, or public use, see the 
        [NLS Historic Maps Subscription API](https://maps.nls.uk/projects/subscription-api/) 
        or email maps@nls.uk.
        """,
        unsafe_allow_html=True,
    )

# Validate numeric inputs before use
try:
    lat_f = float(lat)
    lon_f = float(lon)
    zoom_i = int(zoom)
except ValueError:
    st.error("Latitude, Longitude, and Zoom must be valid numbers.")
    st.stop()

m = leafmap.Map(
    center=[lat_f, lon_f],
    zoom=zoom_i,
    locate_control=True,
    draw_control=False,
    measure_control=False,
)

measure = plugins.MeasureControl(position="bottomleft", active_color="orange")
measure.add_to(m)

if left_name in basemaps:
    left_layer = basemaps[left_name]
else:
    left_layer = folium.TileLayer(
        tiles=links[names.index(left_name)],
        name=left_name,
        attr="National Library of Scotland",
        overlay=True,
    )

if right_name in basemaps:
    right_layer = basemaps[right_name]
else:
    right_layer = folium.TileLayer(
        tiles=links[names.index(right_name)],
        name=right_name,
        attr="National Library of Scotland",
        overlay=True,
    )

if checkbox:
    for index, name in enumerate(names):
        if "OS 25 inch" in name:
            m.add_tile_layer(
                links[index], name, attribution="National Library of Scotland"
            )

m.split_map(left_layer, right_layer)
m.to_streamlit(height=600)