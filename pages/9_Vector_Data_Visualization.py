import os
import fiona
import geopandas as gpd
import pandas as pd
import streamlit as st
import leafmap  # import top-level leafmap
import tempfile
import uuid
import json
from shapely.geometry import Point, Polygon, LineString
import numpy as np

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

# Reliable trusted URLs (known working endpoints)
trusted_urls = [
    "https://raw.githubusercontent.com/giswqs/leafmap/master/examples/data/countries.geojson",
    "https://raw.githubusercontent.com/giswqs/leafmap/master/examples/data/us_cities.csv",
    "https://raw.githubusercontent.com/opengeos/leafmap/master/examples/data/countries.geojson",
    "https://raw.githubusercontent.com/opengeos/streamlit-geospatial/main/data/us_states.geojson",
]

def create_namibia_regions_gdf():
    """Create sample Namibia regions GeoDataFrame with valid polygons"""
    # Define region boundaries as proper polygons (simplified but valid)
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
            Polygon([(18.5, -22.5), (20.5, -22.5), (20.5, -20.5), (18.5, -20.5)])
        ]
    }
    
    gdf = gpd.GeoDataFrame(regions_data, crs="EPSG:4326")
    return gdf


def create_namibia_cities_gdf():
    """Create sample Namibia cities GeoDataFrame with valid points"""
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
                      14.2833, 18.1167, 16.9667, 18.4000, 17.0667]
    }
    
    # Create Point geometries
    geometry = [Point(xy) for xy in zip(cities["longitude"], cities["latitude"])]
    
    # Create DataFrame without the lat/lon columns (they're now in geometry)
    df = pd.DataFrame({
        "name": cities["name"],
        "region": cities["region"],
        "population": cities["population"]
    })
    
    gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")
    return gdf


def create_namibia_roads_gdf():
    """Create sample Namibia roads GeoDataFrame with valid LineStrings"""
    # Define road segments as LineStrings
    roads_data = {
        "name": ["B1 (North)", "B1 (South)", "B2", "B6", "B8", "C28", "C10", "C13"],
        "type": ["National Road", "National Road", "National Road", "National Road", 
                 "National Road", "District Road", "District Road", "District Road"],
        "description": ["Windhoek to Otjiwarongo", "Windhoek to Rehoboth", 
                        "Windhoek to Walvis Bay", "Windhoek to Gobabis",
                        "Rundu to Katima Mulilo", "Swakopmund to Walvis Bay",
                        "Keetmanshoop to Lüderitz", "Otjiwarongo to Outjo"],
        "geometry": [
            LineString([(17.0658, -22.5609), (16.6625, -20.4545)]),
            LineString([(17.0658, -22.5609), (17.0900, -23.3175)]),
            LineString([(17.0658, -22.5609), (14.5053, -22.9575)]),
            LineString([(17.0658, -22.5609), (18.9719, -22.4489)]),
            LineString([(19.7671, -17.9255), (24.2750, -17.5045)]),
            LineString([(14.5279, -22.6783), (14.5053, -22.9575)]),
            LineString([(18.1293, -26.5773), (15.1575, -26.6481)]),
            LineString([(16.6625, -20.4545), (16.1500, -20.1167)])
        ]
    }
    
    gdf = gpd.GeoDataFrame(roads_data, crs="EPSG:4326")
    return gdf


def create_namibia_health_facilities_gdf():
    """Create sample health facilities data"""
    facilities = {
        "name": ["Windhoek Central Hospital", "Katutura Hospital", "Oshakati Hospital",
                 "Rundu Hospital", "Keetmanshoop Hospital", "Walvis Bay Hospital",
                 "Swakopmund Hospital", "Otjiwarongo Hospital", "Tsumeb Hospital",
                 "Gobabis Hospital", "Mariental Hospital", "Lüderitz Hospital"],
        "type": ["Tertiary", "District", "Intermediate",
                 "District", "Intermediate", "District",
                 "District", "District", "District",
                 "District", "District", "District"],
        "beds": [900, 600, 500, 350, 250, 200,
                 180, 220, 140, 120, 100, 80],
        "latitude": [-22.5600, -22.5200, -17.7880,
                     -17.9255, -26.5773, -22.9575,
                     -22.6783, -20.4545, -19.2422,
                     -22.4489, -24.6267, -26.6481],
        "longitude": [17.0660, 17.0600, 15.7050,
                      19.7671, 18.1293, 14.5053,
                      14.5279, 16.6625, 17.7183,
                      18.9719, 17.9378, 15.1575]
    }
    
    geometry = [Point(xy) for xy in zip(facilities["longitude"], facilities["latitude"])]
    
    df = pd.DataFrame({
        "name": facilities["name"],
        "type": facilities["type"],
        "beds": facilities["beds"]
    })
    
    gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")
    return gdf


def create_namibia_schools_gdf():
    """Create sample schools data"""
    np.random.seed(42)
    n_schools = 30
    
    regions = ["Khomas", "Erongo", "Otjozondjupa", "Oshana", "Ohangwena"]
    school_types = ["Primary", "Secondary", "Combined"]
    
    schools = []
    for i in range(n_schools):
        region = np.random.choice(regions)
        
        # Generate coordinates based on region
        if region == "Khomas":
            lat = np.random.uniform(-23.5, -22.0)
            lon = np.random.uniform(16.5, 17.5)
        elif region == "Erongo":
            lat = np.random.uniform(-23.5, -21.5)
            lon = np.random.uniform(14.0, 15.0)
        elif region == "Oshana":
            lat = np.random.uniform(-18.5, -17.5)
            lon = np.random.uniform(15.0, 16.0)
        else:
            lat = np.random.uniform(-22.0, -17.0)
            lon = np.random.uniform(15.0, 20.0)
        
        schools.append({
            "name": f"{region} {np.random.choice(school_types)} School {i+1}",
            "region": region,
            "type": np.random.choice(school_types),
            "enrollment": np.random.randint(200, 1000),
            "latitude": lat,
            "longitude": lon
        })
    
    df = pd.DataFrame(schools)
    geometry = [Point(xy) for xy in zip(df["longitude"], df["latitude"])]
    gdf = gpd.GeoDataFrame(df[["name", "region", "type", "enrollment"]], 
                          geometry=geometry, crs="EPSG:4326")
    return gdf


def is_trusted_url(url):
    """Check if URL is in trusted list"""
    if not url:
        return False
    trusted_domains = [
        "raw.githubusercontent.com",
        "github.com",
        "opengeos.github.io",
        "leafmap.org"
    ]
    return any(domain in url for domain in trusted_domains) or url in trusted_urls


def save_uploaded_file(file_content, file_name):
    """Save uploaded file to temporary directory"""
    _, file_extension = os.path.splitext(file_name)
    file_id = str(uuid.uuid4())
    file_path = os.path.join(tempfile.gettempdir(), f"{file_id}{file_extension}")
    
    with open(file_path, "wb") as f:
        f.write(file_content.getbuffer())
    return file_path


def load_vector_data(file_path):
    """Load vector data from file path or URL with proper driver support"""
    try:
        file_lower = file_path.lower()
        
        # Handle local files that might not exist yet
        if os.path.exists(file_path) or file_path.startswith("http"):
            # Handle KML files
            if file_lower.endswith(".kml"):
                fiona.drvsupport.supported_drivers["KML"] = "rw"
                gdf = gpd.read_file(file_path, driver="KML")
            
            # Handle GeoJSON and JSON
            elif file_lower.endswith(".geojson") or file_lower.endswith(".json"):
                gdf = gpd.read_file(file_path)
            
            # Handle CSV files
            elif file_lower.endswith(".csv"):
                df = pd.read_csv(file_path)
                # Check if it has geometry columns
                if 'latitude' in df.columns and 'longitude' in df.columns:
                    gdf = gpd.GeoDataFrame(
                        df, 
                        geometry=gpd.points_from_xy(df.longitude, df.latitude),
                        crs="EPSG:4326"
                    )
                else:
                    st.error("CSV file must contain latitude and longitude columns")
                    return None
            
            # Handle Shapefile zip
            elif file_lower.endswith(".zip"):
                # Extract to temp directory
                import zipfile
                extract_dir = tempfile.mkdtemp()
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_dir)
                
                # Find .shp file
                shp_files = [f for f in os.listdir(extract_dir) if f.endswith('.shp')]
                if shp_files:
                    shp_path = os.path.join(extract_dir, shp_files[0])
                    gdf = gpd.read_file(shp_path)
                else:
                    st.error("No shapefile found in ZIP archive")
                    return None
            
            # Handle other formats
            else:
                gdf = gpd.read_file(file_path)
            
            return gdf
        else:
            st.error(f"File not found: {file_path}")
            return None
    
    except Exception as e:
        st.error(f"Error loading vector data: {str(e)}")
        return None


def app():
    st.title("Namibia Vector Data Visualization")
    st.markdown(
        """
    Upload and visualize vector datasets (GeoJSON, KML, Shapefile, CSV) for Namibia.
    The app supports multiple plotting backends including **folium**, **kepler.gl**, and **pydeck**.
    """
    )

    row1_col1, row1_col2 = st.columns([2, 1])
    width = 950
    height = 600

    with row1_col2:
        st.subheader("Data Source")
        
        # Create sample datasets
        regions_gdf = create_namibia_regions_gdf()
        cities_gdf = create_namibia_cities_gdf()
        roads_gdf = create_namibia_roads_gdf()
        health_gdf = create_namibia_health_facilities_gdf()
        schools_gdf = create_namibia_schools_gdf()
        
        # Save to temporary GeoJSON files
        temp_dir = tempfile.gettempdir()
        
        # Helper function to save GeoDataFrame safely
        def save_gdf(gdf, filename):
            path = os.path.join(temp_dir, filename)
            gdf.to_file(path, driver="GeoJSON")
            return path
        
        # Sample data options with guaranteed working paths
        sample_data = {
            " Namibia Regions (Polygons)": save_gdf(regions_gdf, "namibia_regions.geojson"),
            "Namibia Cities (Points)": save_gdf(cities_gdf, "namibia_cities.geojson"),
            "Namibia Roads (Lines)": save_gdf(roads_gdf, "namibia_roads.geojson"),
            " Namibia Health Facilities (Points)": save_gdf(health_gdf, "namibia_health.geojson"),
            "Namibia Schools (Points)": save_gdf(schools_gdf, "namibia_schools.geojson"),
            " World Countries (External)": "https://raw.githubusercontent.com/giswqs/leafmap/master/examples/data/countries.geojson",
            " US Cities (External)": "https://raw.githubusercontent.com/giswqs/leafmap/master/examples/data/us_cities.csv",
        }
        
        source_type = st.radio(
            "Choose data source:",
            ["Sample Data", "URL", "Upload File"],
            index=0
        )
        
        backend = st.selectbox(
            "Select plotting backend",
            ["folium", "kepler.gl", "pydeck"],
            index=0
        )

        # Import appropriate backend
        if backend == "folium":
            import leafmap.foliumap as leafmap_backend
            st.info("folium: Best for interactive maps with popups")
        elif backend == "kepler.gl":
            import leafmap.kepler as leafmap_backend
            st.info("kepler.gl: Best for 3D visualizations and large datasets")
        elif backend == "pydeck":
            import leafmap.deck as leafmap_backend
            st.info("pydeck: Best for high-performance WebGL rendering")

        # Handle different source types
        url = None
        uploaded_file = None
        file_path = None
        layer_name = "Vector Layer"

        if source_type == "Sample Data":
            selected_sample = st.selectbox(
                "Select sample dataset",
                list(sample_data.keys()),
                index=0
            )
            file_path = sample_data[selected_sample]
            layer_name = selected_sample.split(" ")[-1].strip("()")
            st.success(f" Selected: {selected_sample}")

        elif source_type == "URL":
            url = st.text_input(
                "Enter URL to vector dataset",
                placeholder="https://example.com/data.geojson"
            )
            
            if url:
                if is_trusted_url(url):
                    st.success(" Trusted URL")
                    file_path = url
                    layer_name = url.split("/")[-1].split(".")[0]
                else:
                    st.warning(" Untrusted URL - proceeding with caution")
                    file_path = url
                    layer_name = url.split("/")[-1].split(".")[0]

        else:  # Upload File
            uploaded_file = st.file_uploader(
                "Upload vector dataset",
                type=["geojson", "kml", "zip", "csv", "json", "shp"],
                help="Supported formats: GeoJSON, KML, Shapefile (as ZIP), CSV"
            )
            
            if uploaded_file:
                file_path = save_uploaded_file(uploaded_file, uploaded_file.name)
                layer_name = os.path.splitext(uploaded_file.name)[0]
                st.success(f" Uploaded: {uploaded_file.name}")

        container = st.container()

    # Load and visualize data
    with row1_col1:
        try:
            if not file_path:
                # No data selected - show empty map
                m = leafmap_backend.Map(center=[-22.0, 17.0], zoom=5)
                if backend == "folium":
                    m.add_basemap("OpenStreetMap")
                    m.to_streamlit(width=width, height=height)
                elif backend == "pydeck":
                    st.pydeck_chart(m)
                else:  # kepler.gl
                    m.to_streamlit(height=height)
                st.info(" Select a data source from the sidebar to begin")
                st.stop()

            # Load the data
            with st.spinner("Loading vector data..."):
                gdf = load_vector_data(file_path)

            if gdf is None:
                st.error("Failed to load data. Please check your file and try again.")
                st.stop()
                
            if gdf.empty:
                st.error("The loaded dataset is empty. Please try another file.")
                st.stop()

            # Display data info
            st.success(f" Successfully loaded {len(gdf)} features")
            
            # Get centroid for map centering
            try:
                total_bounds = gdf.total_bounds
                center_lon = (total_bounds[0] + total_bounds[2]) / 2
                center_lat = (total_bounds[1] + total_bounds[3]) / 2
                lon, lat = center_lon, center_lat
            except:
                # Fallback to Namibia center
                lon, lat = 17.0, -22.0

            # Create map with appropriate backend
            m = leafmap_backend.Map(center=(lat, lon), zoom=6)

            # Add data to map based on backend
            if backend == "pydeck":
                column_names = gdf.columns.values.tolist()
                random_column = None
                
                with container:
                    st.subheader(" Visualization Options")
                    random_color = st.checkbox("Apply random colors", True)
                    if random_color and column_names:
                        # Filter out geometry column
                        str_columns = [col for col in column_names if col != 'geometry']
                        if str_columns:
                            random_column = st.selectbox(
                                "Select column for colors",
                                str_columns,
                                index=0
                            )
                
                # Add to pydeck
                m.add_gdf(gdf, random_color_column=random_column)
                
                # Display with pydeck
                st.pydeck_chart(m)
                
            else:
                # folium or kepler.gl
                with container:
                    st.subheader("🎨 Layer Options")
                    
                    # Style options for folium
                    if backend == "folium":
                        col1, col2 = st.columns(2)
                        with col1:
                            fill_color = st.color_picker("Fill color", "#3388ff")
                            fill_opacity = st.slider("Fill opacity", 0.0, 1.0, 0.5, 0.1)
                        with col2:
                            line_color = st.color_picker("Line color", "#000000")
                            line_weight = st.slider("Line weight", 1, 10, 2)
                        
                        style = {
                            "fillColor": fill_color,
                            "color": line_color,
                            "weight": line_weight,
                            "fillOpacity": fill_opacity
                        }
                    else:
                        style = None
                    
                    show_popups = st.checkbox("Show popups on click", True)
                
                # Add to map
                if backend == "folium" and show_popups:
                    # Get first few columns for tooltips (exclude geometry)
                    tooltip_fields = [col for col in gdf.columns.tolist() if col != 'geometry'][:5]
                    tooltip_aliases = [col.replace('_', ' ').title() for col in tooltip_fields]
                    
                    m.add_gdf(
                        gdf,
                        layer_name=layer_name,
                        style=style,
                        tooltip_fields=tooltip_fields,
                        tooltip_aliases=tooltip_aliases
                    )
                else:
                    # Simple add without tooltips
                    m.add_gdf(gdf, layer_name=layer_name)
                
                # Add basemap and controls
                m.add_basemap("OpenStreetMap")
                m.add_layer_control()
                
                # Zoom to data extent
                try:
                    m.zoom_to_gdf(gdf)
                except:
                    pass
                
                # Display map
                m.to_streamlit(width=width, height=height)

            # Data information expander
            with st.expander("Data Information"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Features", len(gdf))
                with col2:
                    geom_type = gdf.geometry.iloc[0].geom_type if len(gdf) > 0 else "Unknown"
                    st.metric("Geometry Type", geom_type)
                with col3:
                    st.metric("Columns", len(gdf.columns))
                
                st.write("**Column Names:**")
                st.write(", ".join([col for col in gdf.columns if col != 'geometry']))
                
                if len(gdf) > 0:
                    st.write("**Data Preview:**")
                    preview_cols = [col for col in gdf.columns if col != 'geometry'][:5]
                    if preview_cols:
                        st.dataframe(gdf[preview_cols].head(10))

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            import traceback
            st.error(traceback.format_exc())
            
            # Show empty map as fallback
            m = leafmap_backend.Map(center=[-22.0, 17.0], zoom=5)
            if backend == "folium":
                m.add_basemap("OpenStreetMap")
                m.to_streamlit(width=width, height=height)
            elif backend == "pydeck":
                st.pydeck_chart(m)
            else:
                m.to_streamlit(height=height)


if __name__ == "__main__":
    app()