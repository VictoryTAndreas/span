import ee
import json
import streamlit as st
import geemap.foliumap as geemap

service_account = st.secrets["earthengine"]["json"].replace("\\n", "\n")
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


def nlcd():
    row1_col1, row1_col2 = st.columns([3, 1])
    width = 950
    height = 600

    Map = geemap.Map(center=[40, -100], zoom=4)

    years = ["2001", "2004", "2006", "2008", "2011", "2013", "2016", "2019"]

    def getNLCD(year):
        dataset = ee.ImageCollection("USGS/NLCD_RELEASES/2019_REL/NLCD")
        nlcd = dataset.filter(ee.Filter.eq("system:index", year)).first()
        return nlcd.select("landcover")

    with row1_col2:
        selected_year = st.multiselect("Select a year", years)
        add_legend = st.checkbox("Show legend")

    if selected_year:
        for year in selected_year:
            Map.addLayer(getNLCD(year), {}, "NLCD " + year)
        if add_legend:
            Map.add_legend(
                legend_title="NLCD Land Cover Classification",
                builtin_legend="NLCD"
            )

    with row1_col1:
        Map.to_streamlit(width=width, height=height)


def search_data():
    Map = geemap.Map()

    if "ee_assets" not in st.session_state:
        st.session_state["ee_assets"] = []
    if "asset_titles" not in st.session_state:
        st.session_state["asset_titles"] = []

    col1, col2 = st.columns([2, 1])

    with col2:
        keyword = st.text_input("Enter a keyword to search (e.g., elevation)", "")

        if keyword:
            ee_assets = geemap.search_ee_data(keyword)
            asset_titles = [x["title"] for x in ee_assets]
            asset_types = [x["type"] for x in ee_assets]

            if len(ee_assets) > 0:
                st.session_state["ee_assets"] = ee_assets
                st.session_state["asset_titles"] = asset_titles

            dataset = st.selectbox("Select a dataset", asset_titles)

            if dataset is not None and len(ee_assets) > 0:
                index = asset_titles.index(dataset)

                with st.expander("Show dataset details", True):
                    html = geemap.ee_data_html(st.session_state["ee_assets"][index])
                    st.markdown(html.replace("\n", ""), True)

                ee_id = ee_assets[index]["id"]
                uid = ee_assets[index]["uid"]
                asset_type = asset_types[index]

                st.markdown(f"**Earth Engine Snippet:** `{ee_id}`")

                # Build the EE object directly — no intermediate string needed
                if asset_type == "image_collection":
                    ee_asset = ee.ImageCollection(ee_id)
                elif asset_type == "image":
                    ee_asset = ee.Image(ee_id)
                else:
                    ee_asset = ee.FeatureCollection(ee_id)

                vis_params = st.text_input(
                    "Enter visualization parameters as a dictionary", "{}"
                )
                layer_name = st.text_input("Enter a layer name", uid)

                if st.button("Add dataset to map"):
                    try:
                        vis_str = vis_params.strip() or "{}"
                        vis = json.loads(vis_str.replace("'", '"'))
                        if not isinstance(vis, dict):
                            st.error("Visualization parameters must be a dictionary.")
                        else:
                            try:
                                Map.addLayer(ee_asset, vis, layer_name)
                            except Exception as e:
                                st.error(f"Error adding layer: {e}")
                    except Exception as e:
                        st.error(f"Invalid visualization parameters: {e}")

    # Map always renders, keyword or not
    with col1:
        Map.to_streamlit()


def app():
    st.title("Earth Engine Data Catalog")

    apps = [
        "Search Earth Engine Data Catalog",
        "National Land Cover Database (NLCD)",
    ]

    selected_app = st.selectbox("Select an app", apps)

    if selected_app == "National Land Cover Database (NLCD)":
        nlcd()
    elif selected_app == "Search Earth Engine Data Catalog":
        search_data()


app()