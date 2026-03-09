import datetime
import os
import pathlib
import requests
import zipfile
import pandas as pd
import pydeck as pdk
import geopandas as gpd
import streamlit as st
import leafmap.colormaps as cm
from leafmap.common import hex_to_rgb
import xml.etree.ElementTree as ET
from shapely.geometry import Point, Polygon
import json

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
    VTA Namibia at [vtanamibia.com](https://www.vtanamibia.com) | [GitHub](https://github.com/VictoryTAndreas) | [Twitter](https://twitter.com/vicanddotvta) | [YouTube](https://youtube.com/@vtastudios) | [LinkedIn](https://www.linkedin.com/company/vta-labs-studios/?originalSubdomain=na)
    """
)

STREAMLIT_STATIC_PATH = pathlib.Path(st.__path__[0]) / "static"
DOWNLOADS_PATH = STREAMLIT_STATIC_PATH / "downloads"
if not DOWNLOADS_PATH.is_dir():
    DOWNLOADS_PATH.mkdir()

# NSDI Digital Namibia WFS endpoint
NSDI_WFS_URL = "https://digitalnamibia.nsa.org.na/geoserver/ows"

# Namibia administrative boundaries and census data sources
NAMIBIA_DATA = {
    "regions": {
        "wfs_layer": "nsa:namibia_regions_2012",
        "description": "Namibia Regions (2012 boundaries)",
        "geojson_url": "https://raw.githubusercontent.com/VictoryTAndreas/namibia-geodata/main/regions.geojson",
        "local_file": "namibia_regions.geojson"
    },
    "constituencies": {
        "wfs_layer": "nsa:namibia_constituencies_2014",
        "description": "Namibia Constituencies (2014 boundaries)",
        "geojson_url": "https://raw.githubusercontent.com/VictoryTAndreas/namibia-geodata/main/constituencies.geojson",
        "local_file": "namibia_constituencies.geojson"
    },
    "settlements": {
        "wfs_layer": "nsa:namibia_settlements_2011",
        "description": "Namibia Settlements (2011 census)",
        "geojson_url": "https://raw.githubusercontent.com/VictoryTAndreas/namibia-geodata/main/settlements.geojson",
        "local_file": "namibia_settlements.geojson"
    }
}

# Namibia census and demographic data
@st.cache_data
def get_namibia_census_data():
    """Fetch Namibia census and demographic data"""
    data = {
        "region": [
            "Khomas", "Erongo", "Otjozondjupa", "Oshana", "Ohangwena",
            "Omusati", "Oshikoto", "Kavango East", "Kavango West", "Zambezi",
            "Kunene", "Hardap", "Karas", "Omaheke"
        ],
        "population_2011": [
            342141, 150809, 143903, 176674, 245100,
            243166, 181973, 115447, 107905, 90477,
            86856, 79507, 77421, 71000
        ],
        "population_2023": [
            494605, 240206, 201346, 258874, 318305,
            310487, 257302, 172694, 158725, 133892,
            128589, 118523, 115489, 106523
        ],
        "households_2011": [
            96484, 46855, 38897, 42983, 51747,
            51934, 42888, 27230, 25238, 21784,
            19365, 19101, 19784, 16697
        ],
        "households_2023": [
            148381, 72142, 58440, 64826, 77695,
            78230, 64472, 40812, 38088, 32596,
            28942, 29038, 30221, 25136
        ],
        "avg_household_size": [
            3.3, 3.3, 3.4, 4.0, 4.1,
            4.0, 4.0, 4.2, 4.2, 4.1,
            4.4, 4.1, 3.8, 4.2
        ],
        "urban_population_percent": [
            87.5, 89.2, 41.3, 52.1, 8.4,
            9.2, 25.7, 34.8, 15.3, 37.2,
            28.6, 56.8, 79.4, 29.7
        ],
        "male_female_ratio": [
            96.2, 106.5, 99.8, 89.1, 88.4,
            89.6, 91.5, 97.2, 96.8, 95.4,
            106.2, 104.3, 106.8, 102.1
        ],
        "median_age": [
            29.5, 31.2, 24.8, 23.4, 19.2,
            19.8, 22.1, 20.5, 20.1, 21.3,
            24.7, 27.8, 31.5, 23.4
        ]
    }
    return pd.DataFrame(data)


@st.cache_data
def get_namibia_housing_data():
    """Fetch Namibia housing and real estate data"""
    data = {
        "region": [
            "Khomas", "Erongo", "Otjozondjupa", "Oshana", "Ohangwena",
            "Omusati", "Oshikoto", "Kavango East", "Kavango West", "Zambezi",
            "Kunene", "Hardap", "Karas", "Omaheke"
        ],
        "total_dwellings": [
            148381, 72142, 58440, 64826, 77695,
            78230, 64472, 40812, 38088, 32596,
            28942, 29038, 30221, 25136
        ],
        "formal_dwellings": [
            133543, 64928, 46752, 51861, 62156,
            62584, 51578, 32650, 30470, 26077,
            23154, 23230, 24177, 20109
        ],
        "informal_dwellings": [
            14838, 7214, 11688, 12965, 15539,
            15646, 12894, 8162, 7618, 6519,
            5788, 5808, 6044, 5027
        ],
        "average_rent_nad": [
            5500, 6200, 3200, 3800, 2100,
            2200, 2800, 2500, 2300, 2700,
            2900, 3100, 3500, 2800
        ],
        "average_property_value_nad": [
            850000, 920000, 520000, 580000, 350000,
            360000, 440000, 380000, 350000, 400000,
            420000, 460000, 510000, 410000
        ],
        "homeownership_rate": [
            52.3, 48.7, 63.2, 58.4, 71.5,
            72.1, 65.8, 68.4, 69.2, 64.7,
            61.3, 59.8, 57.2, 66.5
        ],
        "housing_density_per_km2": [
            18.5, 5.2, 1.8, 42.3, 38.6,
            36.2, 12.4, 4.8, 3.9, 5.2,
            0.9, 0.7, 0.5, 1.1
        ]
    }
    return pd.DataFrame(data)


@st.cache_data
def get_namibia_economic_data():
    """Fetch Namibia economic indicators by region"""
    data = {
        "region": [
            "Khomas", "Erongo", "Otjozondjupa", "Oshana", "Ohangwena",
            "Omusati", "Oshikoto", "Kavango East", "Kavango West", "Zambezi",
            "Kunene", "Hardap", "Karas", "Omaheke"
        ],
        "employment_rate": [
            68.5, 72.3, 64.2, 62.8, 58.4,
            59.1, 61.5, 57.2, 55.8, 56.4,
            63.7, 66.2, 70.1, 62.5
        ],
        "average_monthly_income_nad": [
            8500, 9200, 6200, 5800, 4200,
            4300, 5100, 4800, 4500, 4700,
            5400, 5900, 6800, 5200
        ],
        "poverty_rate": [
            22.4, 19.8, 32.5, 28.6, 42.3,
            41.5, 35.2, 38.4, 40.2, 36.8,
            31.5, 29.4, 26.7, 34.2
        ],
        "gdp_contribution_percent": [
            28.5, 21.3, 8.2, 7.4, 5.2,
            5.1, 6.3, 4.2, 3.1, 2.8,
            2.5, 2.1, 2.8, 1.5
        ]
    }
    return pd.DataFrame(data)


def create_sample_regions_gdf():
    """Create sample GeoDataFrame for Namibia regions"""
    # Region boundaries (simplified polygons)
    regions_data = {
        "region": [
            "Khomas", "Erongo", "Otjozondjupa", "Oshana", "Ohangwena",
            "Omusati", "Oshikoto", "Kavango East", "Kavango West", "Zambezi",
            "Kunene", "Hardap", "Karas", "Omaheke"
        ],
        "geometry": [
            Polygon([(16.5, -23.5), (17.5, -23.5), (17.5, -22.0), (16.5, -22.0), (16.5, -23.5)]),  # Khomas
            Polygon([(14.0, -23.5), (15.0, -23.5), (15.0, -21.5), (14.0, -21.5), (14.0, -23.5)]),  # Erongo
            Polygon([(17.5, -20.5), (19.0, -20.5), (19.0, -19.0), (17.5, -19.0), (17.5, -20.5)]),  # Otjozondjupa
            Polygon([(15.0, -18.5), (16.0, -18.5), (16.0, -17.5), (15.0, -17.5), (15.0, -18.5)]),  # Oshana
            Polygon([(16.0, -18.0), (17.0, -18.0), (17.0, -17.0), (16.0, -17.0), (16.0, -18.0)]),  # Ohangwena
            Polygon([(14.5, -18.0), (15.5, -18.0), (15.5, -17.0), (14.5, -17.0), (14.5, -18.0)]),  # Omusati
            Polygon([(16.0, -19.5), (17.5, -19.5), (17.5, -18.0), (16.0, -18.0), (16.0, -19.5)]),  # Oshikoto
            Polygon([(20.0, -18.5), (21.5, -18.5), (21.5, -17.5), (20.0, -17.5), (20.0, -18.5)]),  # Kavango East
            Polygon([(18.5, -18.5), (20.0, -18.5), (20.0, -17.5), (18.5, -17.5), (18.5, -18.5)]),  # Kavango West
            Polygon([(23.0, -18.5), (25.0, -18.5), (25.0, -17.0), (23.0, -17.0), (23.0, -18.5)]),  # Zambezi
            Polygon([(12.0, -20.5), (14.0, -20.5), (14.0, -17.0), (12.0, -17.0), (12.0, -20.5)]),  # Kunene
            Polygon([(16.0, -25.5), (18.0, -25.5), (18.0, -23.5), (16.0, -23.5), (16.0, -25.5)]),  # Hardap
            Polygon([(15.0, -28.5), (18.0, -28.5), (18.0, -26.0), (15.0, -26.0), (15.0, -28.5)]),  # Karas
            Polygon([(18.5, -22.5), (20.5, -22.5), (20.5, -20.5), (18.5, -20.5), (18.5, -22.5)])   # Omaheke
        ]
    }
    return gpd.GeoDataFrame(regions_data, crs="EPSG:4326")


def create_sample_constituencies_gdf():
    """Create sample GeoDataFrame for Namibia constituencies"""
    # This is a simplified version - in production, use actual constituency boundaries
    regions_gdf = create_sample_regions_gdf()
    
    # Split each region into 2-3 constituencies (simplified)
    constituencies = []
    for idx, row in regions_gdf.iterrows():
        region = row['region']
        geom = row['geometry']
        bounds = geom.bounds
        
        # Create 2-3 constituencies per region
        n_constituencies = 3 if region in ["Khomas", "Erongo", "Oshana"] else 2
        
        for i in range(n_constituencies):
            # Simplified constituency boundaries (just for demonstration)
            width = (bounds[2] - bounds[0]) / n_constituencies
            const_geom = Polygon([
                (bounds[0] + i * width, bounds[1]),
                (bounds[0] + (i + 1) * width, bounds[1]),
                (bounds[0] + (i + 1) * width, bounds[3]),
                (bounds[0] + i * width, bounds[3]),
                (bounds[0] + i * width, bounds[1])
            ])
            constituencies.append({
                "region": region,
                "constituency": f"{region} Constituency {i+1}",
                "geometry": const_geom
            })
    
    return gpd.GeoDataFrame(constituencies, crs="EPSG:4326")


def create_sample_settlements_gdf():
    """Create sample GeoDataFrame for Namibia settlements"""
    # Major towns/cities in Namibia
    settlements = {
        "settlement": [
            "Windhoek", "Walvis Bay", "Swakopmund", "Oshakati", "Rundu",
            "Otjiwarongo", "Keetmanshoop", "Lüderitz", "Grootfontein", "Tsumeb",
            "Rehoboth", "Katima Mulilo", "Gobabis", "Mariental", "Omaruru"
        ],
        "region": [
            "Khomas", "Erongo", "Erongo", "Oshana", "Kavango East",
            "Otjozondjupa", "Karas", "Karas", "Otjozondjupa", "Oshikoto",
            "Hardap", "Zambezi", "Omaheke", "Hardap", "Erongo"
        ],
        "population": [
            325858, 62096, 44725, 48666, 63431,
            28000, 20977, 12500, 24000, 19000,
            28843, 28500, 19000, 12000, 8500
        ],
        "latitude": [
            -22.5609, -22.9575, -22.6783, -17.7881, -17.9255,
            -20.4545, -26.5773, -26.6481, -19.5725, -19.2422,
            -23.3175, -17.5045, -22.4489, -24.6267, -21.4228
        ],
        "longitude": [
            17.0658, 14.5053, 14.5279, 15.7045, 19.7671,
            16.6625, 18.1293, 15.1575, 18.1167, 17.7183,
            17.0900, 24.2750, 18.9719, 17.9378, 15.9417
        ]
    }
    
    # Create point geometries
    geometry = [Point(xy) for xy in zip(settlements["longitude"], settlements["latitude"])]
    
    gdf = gpd.GeoDataFrame(
        settlements, 
        geometry=geometry,
        crs="EPSG:4326"
    )
    
    return gdf


@st.cache_data
def get_namibia_geodata(level="regions"):
    """Fetch Namibia geospatial data from NSDI or use local data"""
    gdf = None
    
    try:
        # Try to fetch from NSDI WFS first
        import warnings
        warnings.filterwarnings('ignore')
        
        # Check if owslib is available
        try:
            from owslib.wfs import WebFeatureService
            
            wfs = WebFeatureService(url=NSDI_WFS_URL, version='2.0.0', timeout=30)
            layer_name = NAMIBIA_DATA[level]["wfs_layer"]
            
            if layer_name in wfs.contents:
                response = wfs.getfeature(typename=layer_name, outputFormat='application/json')
                gdf = gpd.read_file(response)
                if not gdf.empty:
                    st.success(f"Successfully loaded {level} data from NSDI")
                    return gdf
        except ImportError:
            st.warning("OWSLib not installed. Using local data.")
        except Exception as e:
            st.warning(f"Could not fetch from NSDI WFS: {str(e)}")
    
    except Exception as e:
        st.warning(f"Error accessing NSDI: {str(e)}")
    
    # Fallback to local/cached data
    if gdf is None:
        st.info(f"Using local sample data for {level}")
        
        if level == "regions":
            gdf = create_sample_regions_gdf()
        elif level == "constituencies":
            gdf = create_sample_constituencies_gdf()
        elif level == "settlements":
            gdf = create_sample_settlements_gdf()
        else:
            # Default to regions
            gdf = create_sample_regions_gdf()
    
    return gdf


def join_namibia_data(gdf, df, join_col="region"):
    """Join attribute data with geospatial data"""
    if gdf is None or gdf.empty:
        st.error("No geospatial data available")
        return gpd.GeoDataFrame()
    
    if df is None or df.empty:
        st.error("No attribute data available")
        return gdf
    
    # Ensure the join column exists in both dataframes
    if join_col not in gdf.columns:
        # Try alternative column names
        possible_cols = ['region', 'REGION', 'Region', 'name', 'NAME']
        for col in possible_cols:
            if col in gdf.columns:
                join_col = col
                break
    
    if join_col not in gdf.columns:
        st.error(f"Join column '{join_col}' not found in geospatial data")
        return gdf
    
    gdf_joined = gdf.merge(df, left_on=join_col, right_on="region", how="left")
    return gdf_joined


def app():
    st.title("🏠 Namibia Population, Housing & Market Trends Dashboard")
    st.markdown(
        """
        **Introduction:** This interactive dashboard provides insights into Namibia's demographic, housing, and economic trends 
        at regional and constituency levels. Data sources include the [Namibia Statistics Agency (NSA)](https://nsa.org.na) and 
        the [NSDI Digital Namibia](https://digitalnamibia.nsa.org.na) portal.
        
        **Data includes:**
        - Population statistics (2011 & 2023 census data)
        - Housing characteristics and property values
        - Economic indicators by region
        - Urban/rural distribution
        """
    )

    with st.expander("📹 See a demo"):
        st.image("https://i.imgur.com/Z3dk6Tr.gif")

    # Main controls
    row1_col1, row1_col2, row1_col3, row1_col4 = st.columns([1, 1, 1, 2])
    
    with row1_col1:
        data_category = st.selectbox(
            "Data Category",
            ["Population & Demographics", "Housing & Real Estate", "Economic Indicators"],
            index=0
        )
    
    with row1_col2:
        geographic_level = st.selectbox(
            "Geographic Level",
            ["Regions", "Constituencies", "Settlements"],
            index=0
        )
    
    # Load data based on selection
    if data_category == "Population & Demographics":
        df = get_namibia_census_data()
        available_columns = [col for col in df.columns if col != "region"]
    elif data_category == "Housing & Real Estate":
        df = get_namibia_housing_data()
        available_columns = [col for col in df.columns if col != "region"]
    else:  # Economic Indicators
        df = get_namibia_economic_data()
        available_columns = [col for col in df.columns if col != "region"]
    
    with row1_col3:
        selected_col = st.selectbox(
            "Select Indicator",
            available_columns,
            index=0
        )
    
    with row1_col4:
        show_desc = st.checkbox("Show indicator description")
        if show_desc:
            descriptions = {
                "population_2011": "Total population count from 2011 Census",
                "population_2023": "Projected population for 2023",
                "households_2011": "Number of households from 2011 Census",
                "households_2023": "Projected number of households for 2023",
                "avg_household_size": "Average number of persons per household",
                "urban_population_percent": "Percentage of population living in urban areas",
                "male_female_ratio": "Number of males per 100 females",
                "median_age": "Median age of population",
                "total_dwellings": "Total number of dwelling units",
                "formal_dwellings": "Number of formal/structured dwellings",
                "informal_dwellings": "Number of informal dwellings/shacks",
                "average_rent_nad": "Average monthly rent in Namibian Dollars",
                "average_property_value_nad": "Average property value in Namibian Dollars",
                "homeownership_rate": "Percentage of households owning their home",
                "housing_density_per_km2": "Number of dwellings per square kilometer",
                "employment_rate": "Percentage of working-age population employed",
                "average_monthly_income_nad": "Average monthly income in Namibian Dollars",
                "poverty_rate": "Percentage of population below poverty line",
                "gdp_contribution_percent": "Region's contribution to national GDP"
            }
            desc = descriptions.get(selected_col, "No description available")
            st.markdown(f"**📊 {selected_col.replace('_', ' ').title()}**")
            st.markdown(f"*{desc}*")

    # Load geospatial data
    level_key = geographic_level.lower()
    gdf = get_namibia_geodata(level_key)
    
    if gdf is None or gdf.empty:
        st.error("Failed to load geospatial data. Please try again later.")
        st.stop()

    # Join data
    gdf_joined = join_namibia_data(gdf, df)
    
    if gdf_joined is None or gdf_joined.empty:
        st.error("Failed to join data. Please check your data sources.")
        st.stop()

    # Visualization controls
    row2_col1, row2_col2, row2_col3, row2_col4, row2_col5 = st.columns([1, 1, 1, 1, 2])

    palettes = cm.list_colormaps()
    with row2_col1:
        palette = st.selectbox("Color palette", palettes, index=palettes.index("YlOrRd"))
    with row2_col2:
        n_colors = st.slider("Number of colors", min_value=2, max_value=20, value=8)
    with row2_col3:
        show_nodata = st.checkbox("Show nodata areas", value=True)
    with row2_col4:
        show_3d = st.checkbox("Show 3D view", value=False)
    with row2_col5:
        if show_3d:
            elev_scale = st.slider(
                "Elevation scale", min_value=1, max_value=1000000, value=100, step=10
            )
        else:
            elev_scale = 1

    # Split data into with/without values
    gdf_null = gdf_joined[gdf_joined[selected_col].isna()].copy()
    gdf_values = gdf_joined[~gdf_joined[selected_col].isna()].copy()
    
    if not gdf_values.empty:
        gdf_values = gdf_values.sort_values(by=selected_col, ascending=True)

        # Generate colors
        colors = cm.get_palette(palette, n_colors)
        colors = [hex_to_rgb(c) for c in colors]

        for i, ind in enumerate(gdf_values.index):
            if len(gdf_values) > 0:
                index = int(i / (len(gdf_values) / len(colors)))
                if index >= len(colors):
                    index = len(colors) - 1
                gdf_values.loc[ind, "R"] = colors[index][0]
                gdf_values.loc[ind, "G"] = colors[index][1]
                gdf_values.loc[ind, "B"] = colors[index][2]

    # Initial view state centered on Namibia
    initial_view_state = pdk.ViewState(
        latitude=-22.0,
        longitude=17.0,
        zoom=5,
        max_zoom=16,
        pitch=0 if not show_3d else 45,
        bearing=0,
        height=900,
        width=None,
    )

    min_value = gdf_values[selected_col].min() if not gdf_values.empty else 0
    max_value = gdf_values[selected_col].max() if not gdf_values.empty else 1
    
    color_exp = f"[R, G, B]"

    # Main GeoJSON layer
    geojson = pdk.Layer(
        "GeoJsonLayer",
        gdf_values,
        pickable=True,
        opacity=0.7,
        stroked=True,
        filled=True,
        extruded=show_3d,
        wireframe=True,
        get_elevation=f"{selected_col}",
        elevation_scale=elev_scale,
        get_fill_color=color_exp,
        get_line_color=[0, 0, 0],
        get_line_width=2,
        line_width_min_pixels=1,
    )

    # No-data areas layer
    geojson_null = pdk.Layer(
        "GeoJsonLayer",
        gdf_null,
        pickable=True,
        opacity=0.2,
        stroked=True,
        filled=True,
        extruded=False,
        wireframe=True,
        get_fill_color=[200, 200, 200],
        get_line_color=[0, 0, 0],
        get_line_width=2,
        line_width_min_pixels=1,
    )

    # Tooltip - determine which name column to use
    name_col = 'region' if 'region' in gdf_values.columns else 'constituency' if 'constituency' in gdf_values.columns else 'settlement' if 'settlement' in gdf_values.columns else 'NAME'
    
    tooltip = {
        "html": f"<b>{{{name_col}}}</b><br><b>"
        + selected_col.replace('_', ' ').title()
        + ":</b> {"
        + selected_col
        + ":,.0f}<br>",
        "style": {"backgroundColor": "steelblue", "color": "white"},
    }

    layers = [geojson]
    if show_nodata and not gdf_null.empty:
        layers.append(geojson_null)

    r = pdk.Deck(
        layers=layers,
        initial_view_state=initial_view_state,
        map_style="light",
        tooltip=tooltip,
    )

    row3_col1, row3_col2 = st.columns([6, 1])

    with row3_col1:
        st.pydeck_chart(r)
    with row3_col2:
        if not gdf_values.empty:
            st.write(
                cm.create_colormap(
                    palette,
                    label=selected_col.replace("_", " ").title(),
                    width=0.2,
                    height=3,
                    orientation="vertical",
                    vmin=min_value,
                    vmax=max_value,
                    font_size=10,
                )
            )

    # Data table section
    row4_col1, row4_col2 = st.columns([1, 3])
    with row4_col1:
        show_data = st.checkbox("Show raw data table")
    with row4_col2:
        if show_data and not gdf_values.empty:
            show_cols = st.multiselect(
                "Select columns to display",
                [name_col] + available_columns,
                default=[name_col, selected_col]
            )
    
    if show_data and not gdf_values.empty:
        st.dataframe(
            gdf_values[show_cols].style.format({
                col: '{:,.0f}' for col in available_columns 
                if col in show_cols and gdf_values[col].dtype in ['int64', 'float64']
            })
        )
        
        # Summary statistics
        if not gdf_values.empty and selected_col in gdf_values.columns:
            st.subheader(" Summary Statistics")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Mean", f"{gdf_values[selected_col].mean():,.0f}")
            with col2:
                st.metric("Median", f"{gdf_values[selected_col].median():,.0f}")
            with col3:
                st.metric("Min", f"{gdf_values[selected_col].min():,.0f}")
            with col4:
                st.metric("Max", f"{gdf_values[selected_col].max():,.0f}")

    # Footer with data sources
    st.markdown("---")
    st.markdown(
        """
        ** Data Sources:**
        - Namibia Statistics Agency (NSA) - Census 2011 & projections
        - NSDI Digital Namibia - Geospatial boundaries
        - Ministry of Urban and Rural Development - Housing statistics
        - Bank of Namibia - Economic indicators
        
        *Note: Some data points are simulated for demonstration. Contact NSA for official statistics.*
        """
    )


if __name__ == "__main__":
    app()