import os
import zipfile
import fiona
import geopandas as gpd
import pandas as pd
import numpy as np
import streamlit as st
import tempfile
import uuid
import json
from shapely.geometry import Point, Polygon, LineString

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

trusted_domains = [
    "raw.githubusercontent.com",
    "github.com",
    "opengeos.github.io",
    "leafmap.org",
]


def create_namibia_regions_gdf():
    regions_data = {
        "name": ["Khomas", "Erongo", "Otjozondjupa", "Oshana", "Ohangwena",
                 "Omusati", "Oshikoto", "Kavango East", "Kavango West", "Zambezi",
                 "Kunene", "Hardap", "Karas", "Omaheke"],
        "capital": ["Windhoek", "Swakopmund", "Otjiwarongo", "Oshakati", "Eenhana",
                    "Outapi", "Omuthiya", "Rundu", "Nkurenkuru", "Katima Mulilo",
                    "Khorixas", "Mariental", "Keetmanshoop", "Gobabis"],
        "population_2023": [494605, 240206, 201346, 258874, 318305,
                            310487, 257302, 172694, 158725, 133892,
                            128589, 118523, 115489, 106523],
        "area_km2": [36967, 63539, 105327, 8647, 10582,
                     26551, 38685, 43418, 23471, 14785,
                     115260, 109651, 161215, 84731],
        "geometry": [
            Polygon([(16.5, -23.5), (17.5, -23.5), (17.5, -22.0), (16.5, -22.0)]),
            Polygon([(14.0, -23.5), (15.0, -23.5), (15.0, -21.5), (14.0, -21.5)]),
            Polygon([(17.5, -20.5), (19.0, -20.5), (19.0, -19.0), (17.5, -19.0)]),
            Polygon([(15.0, -18.5), (16.0, -18.5), (16.0, -17.5), (15.0, -17.5)]),
            Polygon([(16.0, -18.0), (17.0, -18.0), (17.0, -17.0), (16.0, -17.0)]),
            Polygon([(14.5, -18.0), (15.5, -18.0), (15.5, -17.0), (14.5, -17.0)]),
            Polygon([(16.0, -19.5), (17.5, -19.5), (17.5, -18.0), (16.0, -18.0)]),
            Polygon([(20.0, -18.5), (21.5, -18.5), (21.5, -17.5), (20.0, -17.5)]),
            Polygon([(18.5, -18.5), (20.0, -18.5), (20.0, -17.5), (18.5, -17.5)]),
            Polygon([(23.0, -18.5), (25.0, -18.5), (25.0, -17.0), (23.0, -17.0)]),
            Polygon([(12.0, -20.5), (14.0, -20.5), (14.0, -17.0), (12.0, -17.0)]),
            Polygon([(16.0, -25.5), (18.0, -25.5), (18.0, -23.5), (16.0, -23.5)]),
            Polygon([(15.0, -28.5), (18.0, -28.5), (18.0, -26.0), (15.0, -26.0)]),
            Polygon([(18.5, -22.5), (20.5, -22.5), (20.5, -20.5), (18.5, -20.5)]),
        ],
    }
    return gpd.GeoDataFrame(regions_data, crs="EPSG:4326")


def create_namibia_cities_gdf():
    cities = {
        "name": ["Windhoek", "Walvis Bay", "Swakopmund", "Oshakati", "Rundu",
                 "Otjiwarongo", "Keetmanshoop", "Lüderitz", "Grootfontein", "Tsumeb",
                 "Rehoboth", "Katima Mulilo", "Gobabis", "Mariental", "Omaruru",
                 "Okahandja", "Outjo", "Opuwo", "Eenhana", "Ondangwa",
                 "Henties Bay", "Karasburg", "Maltahöhe", "Aranos", "Otavi"],
        "region": ["Khomas", "Erongo", "Erongo", "Oshana", "Kavango East",
                   "Otjozondjupa", "Karas", "Karas", "Otjozondjupa", "Oshikoto",
                   "Hardap", "Zambezi", "Omaheke", "Hardap", "Erongo",
                   "Otjozondjupa", "Kunene", "Kunene", "Ohangwena", "Oshana",
                   "Erongo", "Karas", "Hardap", "Hardap", "Otjozondjupa"],
        "population": [431000, 102000, 55000, 52000, 68000,
                       35000, 27000, 16000, 28000, 24000,
                       32000, 31000, 22000, 14000, 9000,
                       26000, 9000, 6000, 6500, 28000,
                       8000, 5500, 2000, 2500, 5000],
        "latitude": [-22.5609, -22.9575, -22.6783, -17.7881, -17.9255,
                     -20.4545, -26.5773, -26.6481, -19.5725, -19.2422,
                     -23.3175, -17.5045, -22.4489, -24.6267, -21.4228,
                     -21.9833, -20.1167, -18.0500, -17.4667, -17.9167,
                     -22.1167, -26.6500, -24.8333, -24.1500, -19.6333],
        "longitude": [17.0658, 14.5053, 14.5279, 15.7045, 19.7671,
                      16.6625, 18.1293, 15.1575, 18.1167, 17.7183,
                      17.0900, 24.2750, 18.9719, 17.9378, 15.9417,
                      16.9167, 16.1500, 13.8333, 16.4667, 15.9500,
                      14.2833, 18.1167, 16.9667, 18.4000, 17.0667],
    }
    geometry = [Point(lon, lat) for lon, lat in zip(cities["longitude"], cities["latitude"])]
    df = pd.DataFrame({k: cities[k] for k in ["name", "region", "population"]})
    return gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")


def create_namibia_roads_gdf():
    roads_data = {
        "name": ["B1 (North)", "B1 (South)", "B2", "B6", "B8", "C28", "C10", "C13"],
        "type": ["National Road"] * 5 + ["District Road"] * 3,
        "description": [
            "Windhoek to Otjiwarongo", "Windhoek to Rehoboth",
            "Windhoek to Walvis Bay", "Windhoek to Gobabis",
            "Rundu to Katima Mulilo", "Swakopmund to Walvis Bay",
            "Keetmanshoop to Lüderitz", "Otjiwarongo to Outjo",
        ],
        "geometry": [
            LineString([(17.0658, -22.5609), (16.6625, -20.4545)]),
            LineString([(17.0658, -22.5609), (17.0900, -23.3175)]),
            LineString([(17.0658, -22.5609), (14.5053, -22.9575)]),
            LineString([(17.0658, -22.5609), (18.9719, -22.4489)]),
            LineString([(19.7671, -17.9255), (24.2750, -17.5045)]),
            LineString([(14.5279, -22.6783), (14.5053, -22.9575)]),
            LineString([(18.1293, -26.5773), (15.1575, -26.6481)]),
            LineString([(16.6625, -20.4545), (16.1500, -20.1167)]),
        ],
    }
    return gpd.GeoDataFrame(roads_data, crs="EPSG:4326")


def create_namibia_health_facilities_gdf():
    facilities = {
        "name": ["Windhoek Central Hospital", "Katutura Hospital", "Oshakati Hospital",
                 "Rundu Hospital", "Keetmanshoop Hospital", "Walvis Bay Hospital",
                 "Swakopmund Hospital", "Otjiwarongo Hospital", "Tsumeb Hospital",
                 "Gobabis Hospital", "Mariental Hospital", "Lüderitz Hospital"],
        "type": ["Tertiary", "District", "Intermediate", "District", "Intermediate",
                 "District", "District", "District", "District", "District", "District", "District"],
        "beds": [900, 600, 500, 350, 250, 200, 180, 220, 140, 120, 100, 80],
        "latitude": [-22.5600, -22.5200, -17.7880, -17.9255, -26.5773, -22.9575,
                     -22.6783, -20.4545, -19.2422, -22.4489, -24.6267, -26.6481],
        "longitude": [17.0660, 17.0600, 15.7050, 19.7671, 18.1293, 14.5053,
                      14.5279, 16.6625, 17.7183, 18.9719, 17.9378, 15.1575],
    }
    geometry = [Point(lon, lat) for lon, lat in zip(facilities["longitude"], facilities["latitude"])]
    df = pd.DataFrame({k: facilities[k] for k in ["name", "type", "beds"]})
    return gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")


def create_namibia_schools_gdf():
    np.random.seed(42)
    n_schools = 30
    regions = ["Khomas", "Erongo", "Otjozondjupa", "Oshana", "Ohangwena"]
    school_types = ["Primary", "Secondary", "Combined"]
    region_bounds = {
        "Khomas":      (-23.5, -22.0, 16.5, 17.5),
        "Erongo":      (-23.5, -21.5, 14.0, 15.0),
        "Oshana":      (-18.5, -17.5, 15.0, 16.0),
        "Otjozondjupa": (-22.0, -17.0, 15.0, 20.0),
        "Ohangwena":   (-22.0, -17.0, 15.0, 20.0),
    }
    schools = []
    for i in range(n_schools):
        region = np.random.choice(regions)
        lat_min, lat_max, lon_min, lon_max = region_bounds[region]
        schools.append({
            "name": f"{region} {np.random.choice(school_types)} School {i+1}",
            "region": region,
            "type": np.random.choice(school_types),
            "enrollment": np.random.randint(200, 1000),
            "latitude": np.random.uniform(lat_min, lat_max),
            "longitude": np.random.uniform(lon_min, lon_max),
        })
    df = pd.DataFrame(schools)
    geometry = [Point(lon, lat) for lon, lat in zip(df["longitude"], df["latitude"])]
    return gpd.GeoDataFrame(
        df[["name", "region", "type", "enrollment"]], geometry=geometry, crs="EPSG:4326"
    )


def is_trusted_url(url):
    if not url:
        return False
    return any(domain in url for domain in trusted_domains)


def save_uploaded_file(file_content, file_name):
    _, ext = os.path.splitext(file_name)
    file_path = os.path.join(tempfile.gettempdir(), f"{uuid.uuid4()}{ext}")
    with open(file_path, "wb") as f:
        f.write(file_content.getbuffer())
    return file_path


def load_vector_data(file_path):
    try:
        file_lower = file_path.lower()
        if not (os.path.exists(file_path) or file_path.startswith("http")):
            st.error(f"File not found: {file_path}")
            return None

        if file_lower.endswith(".kml"):
            fiona.drvsupport.supported_drivers["KML"] = "rw"
            return gpd.read_file(file_path, driver="KML")
        elif file_lower.endswith((".geojson", ".json")):
            return gpd.read_file(file_path)
        elif file_lower.endswith(".csv"):
            df = pd.read_csv(file_path)
            if "latitude" in df.columns and "longitude" in df.columns:
                return gpd.GeoDataFrame(
                    df,
                    geometry=gpd.points_from_xy(df.longitude, df.latitude),
                    crs="EPSG:4326",
                )
            st.error("CSV must contain latitude and longitude columns.")
            return None
        elif file_lower.endswith(".zip"):
            extract_dir = tempfile.mkdtemp()
            with zipfile.ZipFile(file_path, "r") as zf:
                zf.extractall(extract_dir)
            shp_files = [f for f in os.listdir(extract_dir) if f.endswith(".shp")]
            if shp_files:
                return gpd.read_file(os.path.join(extract_dir, shp_files[0]))
            st.error("No shapefile found in ZIP archive.")
            return None
        else:
            return gpd.read_file(file_path)

    except Exception as e:
        st.error(f"Error loading vector data: {e}")
        return None


def get_backend(backend_name):
    if backend_name == "folium":
        import leafmap.foliumap as lb
        return lb
    elif backend_name == "kepler.gl":
        import leafmap.kepler as lb
        return lb
    elif backend_name == "pydeck":
        import leafmap.deck as lb
        return lb


def app():
    st.title("Namibia Vector Data Visualization")
    st.markdown(
        "Upload and visualize vector datasets (GeoJSON, KML, Shapefile, CSV) for Namibia. "
        "Supports **folium**, **kepler.gl**, and **pydeck** backends."
    )

    width, height = 950, 600
    row1_col1, row1_col2 = st.columns([2, 1])

    temp_dir = tempfile.gettempdir()

    def save_gdf(gdf, filename):
        path = os.path.join(temp_dir, filename)
        gdf.to_file(path, driver="GeoJSON")
        return path

    sample_data = {
        "Namibia Regions (Polygons)": save_gdf(create_namibia_regions_gdf(), "namibia_regions.geojson"),
        "Namibia Cities (Points)": save_gdf(create_namibia_cities_gdf(), "namibia_cities.geojson"),
        "Namibia Roads (Lines)": save_gdf(create_namibia_roads_gdf(), "namibia_roads.geojson"),
        "Namibia Health Facilities (Points)": save_gdf(create_namibia_health_facilities_gdf(), "namibia_health.geojson"),
        "Namibia Schools (Points)": save_gdf(create_namibia_schools_gdf(), "namibia_schools.geojson"),
        "World Countries (External)": "https://raw.githubusercontent.com/giswqs/leafmap/master/examples/data/countries.geojson",
        "US Cities (External)": "https://raw.githubusercontent.com/giswqs/leafmap/master/examples/data/us_cities.csv",
    }

    with row1_col2:
        st.subheader("Data Source")

        backend_name = st.selectbox(
            "Select plotting backend",
            ["folium", "kepler.gl", "pydeck"],
            index=0,
        )
        backend_info = {
            "folium": "Best for interactive maps with popups",
            "kepler.gl": "Best for 3D visualizations and large datasets",
            "pydeck": "Best for high-performance WebGL rendering",
        }
        st.info(backend_info[backend_name])

        leafmap_backend = get_backend(backend_name)

        source_type = st.radio("Choose data source:", ["Sample Data", "URL", "Upload File"])

        file_path = None
        layer_name = "Vector Layer"

        if source_type == "Sample Data":
            selected_sample = st.selectbox("Select sample dataset", list(sample_data.keys()))
            file_path = sample_data[selected_sample]
            layer_name = selected_sample
            st.success(f"Selected: {selected_sample}")

        elif source_type == "URL":
            url = st.text_input("Enter URL to vector dataset", placeholder="https://example.com/data.geojson")
            if url:
                trusted = is_trusted_url(url)
                st.success("Trusted URL") if trusted else st.warning("Untrusted URL — proceeding with caution")
                file_path = url
                layer_name = url.split("/")[-1].split(".")[0]

        else:
            uploaded_file = st.file_uploader(
                "Upload vector dataset",
                type=["geojson", "kml", "zip", "csv", "json", "shp"],
                help="Supported: GeoJSON, KML, Shapefile (ZIP), CSV",
            )
            if uploaded_file:
                file_path = save_uploaded_file(uploaded_file, uploaded_file.name)
                layer_name = os.path.splitext(uploaded_file.name)[0]
                st.success(f"Uploaded: {uploaded_file.name}")

        # Style/visualization options (rendered in sidebar col, shown above map)
        st.subheader("Visualization Options")
        fill_color = "#3388ff"
        line_color = "#000000"
        fill_opacity = 0.5
        line_weight = 2
        random_column = None
        show_popups = False

        if backend_name == "folium":
            c1, c2 = st.columns(2)
            with c1:
                fill_color = st.color_picker("Fill color", "#3388ff")
                fill_opacity = st.slider("Fill opacity", 0.0, 1.0, 0.5, 0.1)
            with c2:
                line_color = st.color_picker("Line color", "#000000")
                line_weight = st.slider("Line weight", 1, 10, 2)
            show_popups = st.checkbox("Show popups on click", True)

        elif backend_name == "pydeck":
            random_color = st.checkbox("Apply random colors", True)
            # random_column selected after data load below

    with row1_col1:
        if not file_path:
            m = leafmap_backend.Map(center=[-22.0, 17.0], zoom=5)
            if backend_name == "folium":
                m.add_basemap("OpenStreetMap")
                m.to_streamlit(width=width, height=height)
            elif backend_name == "pydeck":
                st.pydeck_chart(m)
            else:
                m.to_streamlit(height=height)
            st.info("Select a data source to begin.")
            st.stop()

        with st.spinner("Loading vector data..."):
            gdf = load_vector_data(file_path)

        if gdf is None or gdf.empty:
            st.error("Failed to load data or dataset is empty.")
            st.stop()

        st.success(f"Loaded {len(gdf)} features")

        try:
            b = gdf.total_bounds
            center_lat = (b[1] + b[3]) / 2
            center_lon = (b[0] + b[2]) / 2
        except Exception:
            center_lat, center_lon = -22.0, 17.0

        m = leafmap_backend.Map(center=(center_lat, center_lon), zoom=6)

        if backend_name == "pydeck":
            data_cols = [c for c in gdf.columns if c != "geometry"]
            if random_color and data_cols:
                random_column = st.selectbox("Select column for colors", data_cols)
            m.add_gdf(gdf, random_color_column=random_column)
            st.pydeck_chart(m)

        else:
            style = {
                "fillColor": fill_color,
                "color": line_color,
                "weight": line_weight,
                "fillOpacity": fill_opacity,
            } if backend_name == "folium" else None

            if backend_name == "folium" and show_popups:
                tooltip_fields = [c for c in gdf.columns if c != "geometry"][:5]
                tooltip_aliases = [c.replace("_", " ").title() for c in tooltip_fields]
                m.add_gdf(
                    gdf,
                    layer_name=layer_name,
                    style=style,
                    tooltip_fields=tooltip_fields,
                    tooltip_aliases=tooltip_aliases,
                )
            else:
                m.add_gdf(gdf, layer_name=layer_name)

            m.add_basemap("OpenStreetMap")
            m.add_layer_control()

            try:
                m.zoom_to_gdf(gdf)
            except Exception:
                pass

            m.to_streamlit(width=width, height=height)

        with st.expander("Data Information"):
            c1, c2, c3 = st.columns(3)
            c1.metric("Features", len(gdf))
            c2.metric("Geometry Type", gdf.geometry.iloc[0].geom_type if len(gdf) > 0 else "Unknown")
            c3.metric("Columns", len(gdf.columns))
            data_cols = [c for c in gdf.columns if c != "geometry"]
            st.write("**Columns:**", ", ".join(data_cols))
            if data_cols:
                st.dataframe(gdf[data_cols[:5]].head(10))


app()