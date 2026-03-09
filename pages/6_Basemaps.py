import streamlit as st
import leafmap.foliumap as leafmap
import pandas as pd

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


def get_namibia_basemaps():
    """Return a dictionary of Namibia-specific basemaps and services"""
    
    namibia_basemaps = {
        # NSDI Digital Namibia Base Maps
        "NSDI Digital Namibia - Satellite": {
            "url": "https://digitalnamibia.nsa.org.na/geoserver/gwc/service/wmts?layer=nsa:na_imagery&style=&tilematrixset=EPSG:900913&Service=WMTS&Request=GetTile&Version=1.0.0&Format=image/png&TileMatrix=EPSG:900913:{z}&TileCol={x}&TileRow={y}",
            "attribution": "NSDI Digital Namibia",
            "name": "NSDI Satellite Imagery",
            "type": "Namibia"
        },
        "NSDI Digital Namibia - Topographic": {
            "url": "https://digitalnamibia.nsa.org.na/geoserver/gwc/service/wmts?layer=nsa:na_topographic&style=&tilematrixset=EPSG:900913&Service=WMTS&Request=GetTile&Version=1.0.0&Format=image/png&TileMatrix=EPSG:900913:{z}&TileCol={x}&TileRow={y}",
            "attribution": "NSDI Digital Namibia",
            "name": "NSDI Topographic",
            "type": "Namibia"
        },
        "NSDI Digital Namibia - Administrative Boundaries": {
            "url": "https://digitalnamibia.nsa.org.na/geoserver/gwc/service/wmts?layer=nsa:na_boundaries&style=&tilematrixset=EPSG:900913&Service=WMTS&Request=GetTile&Version=1.0.0&Format=image/png&TileMatrix=EPSG:900913:{z}&TileCol={x}&TileRow={y}",
            "attribution": "NSDI Digital Namibia",
            "name": "NSDI Boundaries",
            "type": "Namibia"
        },
        "NSDI Digital Namibia - Land Cover": {
            "url": "https://digitalnamibia.nsa.org.na/geoserver/gwc/service/wmts?layer=nsa:na_landcover&style=&tilematrixset=EPSG:900913&Service=WMTS&Request=GetTile&Version=1.0.0&Format=image/png&TileMatrix=EPSG:900913:{z}&TileCol={x}&TileRow={y}",
            "attribution": "NSDI Digital Namibia",
            "name": "NSDI Land Cover",
            "type": "Namibia"
        },
        
        # Namibia Statistics Agency - Census Maps
        "NSA - Census 2011 Population Density": {
            "url": "https://digitalnamibia.nsa.org.na/geoserver/NSA/wms?service=WMS&version=1.1.0&request=GetMap&layers=NSA:population_density_2011&bbox=11.5,-29.0,25.5,-16.5&width=768&height=768&srs=EPSG:4326&format=application/openlayers",
            "attribution": "Namibia Statistics Agency",
            "name": "NSA Population Density",
            "type": "Namibia"
        },
        
        # Ministry of Agriculture, Water and Land Reform
        "MAWLR - Agricultural Regions": {
            "url": "https://digitalnamibia.nsa.org.na/geoserver/MAWLR/wms?service=WMS&version=1.1.0&request=GetMap&layers=MAWLR:agricultural_zones&bbox=11.5,-29.0,25.5,-16.5&width=768&height=768&srs=EPSG:4326&format=application/openlayers",
            "attribution": "Ministry of Agriculture",
            "name": "Agricultural Zones",
            "type": "Namibia"
        },
        "MAWLR - Irrigation Schemes": {
            "url": "https://digitalnamibia.nsa.org.na/geoserver/MAWLR/wms?service=WMS&version=1.1.0&request=GetMap&layers=MAWLR:irrigation_schemes&bbox=11.5,-29.0,25.5,-16.5&width=768&height=768&srs=EPSG:4326&format=application/openlayers",
            "attribution": "Ministry of Agriculture",
            "name": "Irrigation Schemes",
            "type": "Namibia"
        },
        
        # Ministry of Mines and Energy
        "MME - Geological Map": {
            "url": "https://digitalnamibia.nsa.org.na/geoserver/MME/wms?service=WMS&version=1.1.0&request=GetMap&layers=MME:geological_map&bbox=11.5,-29.0,25.5,-16.5&width=768&height=768&srs=EPSG:4326&format=application/openlayers",
            "attribution": "Ministry of Mines and Energy",
            "name": "Geological Map",
            "type": "Namibia"
        },
        "MME - Mining Licenses": {
            "url": "https://digitalnamibia.nsa.org.na/geoserver/MME/wms?service=WMS&version=1.1.0&request=GetMap&layers=MME:mining_licenses&bbox=11.5,-29.0,25.5,-16.5&width=768&height=768&srs=EPSG:4326&format=application/openlayers",
            "attribution": "Ministry of Mines and Energy",
            "name": "Mining Licenses",
            "type": "Namibia"
        },
        "MME - Petroleum Exploration": {
            "url": "https://digitalnamibia.nsa.org.na/geoserver/MME/wms?service=WMS&version=1.1.0&request=GetMap&layers=MME:petroleum_exploration&bbox=11.5,-29.0,25.5,-16.5&width=768&height=768&srs=EPSG:4326&format=application/openlayers",
            "attribution": "Ministry of Mines and Energy",
            "name": "Petroleum Exploration",
            "type": "Namibia"
        },
        
        # Ministry of Environment, Forestry and Tourism
        "MEFT - National Parks": {
            "url": "https://digitalnamibia.nsa.org.na/geoserver/MEFT/wms?service=WMS&version=1.1.0&request=GetMap&layers=MEFT:national_parks&bbox=11.5,-29.0,25.5,-16.5&width=768&height=768&srs=EPSG:4326&format=application/openlayers",
            "attribution": "Ministry of Environment",
            "name": "National Parks",
            "type": "Namibia"
        },
        "MEFT - Conservancies": {
            "url": "https://digitalnamibia.nsa.org.na/geoserver/MEFT:wms?service=WMS&version=1.1.0&request=GetMap&layers=MEFT:conservancies&bbox=11.5,-29.0,25.5,-16.5&width=768&height=768&srs=EPSG:4326&format=application/openlayers",
            "attribution": "Ministry of Environment",
            "name": "Communal Conservancies",
            "type": "Namibia"
        },
        "MEFT - Forest Reserves": {
            "url": "https://digitalnamibia.nsa.org.na/geoserver/MEFT/wms?service=WMS&version=1.1.0&request=GetMap&layers=MEFT:forest_reserves&bbox=11.5,-29.0,25.5,-16.5&width=768&height=768&srs=EPSG:4326&format=application/openlayers",
            "attribution": "Ministry of Environment",
            "name": "Forest Reserves",
            "type": "Namibia"
        },
        
        # Ministry of Lands and Resettlement
        "MLR - Land Tenure": {
            "url": "https://digitalnamibia.nsa.org.na/geoserver/MLR/wms?service=WMS&version=1.1.0&request=GetMap&layers=MLR:land_tenure&bbox=11.5,-29.0,25.5,-16.5&width=768&height=768&srs=EPSG:4326&format=application/openlayers",
            "attribution": "Ministry of Lands",
            "name": "Land Tenure",
            "type": "Namibia"
        },
        "MLR - Resettlement Farms": {
            "url": "https://digitalnamibia.nsa.org.na/geoserver/MLR/wms?service=WMS&version=1.1.0&request=GetMap&layers=MLR:resettlement_farms&bbox=11.5,-29.0,25.5,-16.5&width=768&height=768&srs=EPSG:4326&format=application/openlayers",
            "attribution": "Ministry of Lands",
            "name": "Resettlement Farms",
            "type": "Namibia"
        },
        
        # Ministry of Works and Transport
        "MWT - National Road Network": {
            "url": "https://digitalnamibia.nsa.org.na/geoserver/MWT/wms?service=WMS&version=1.1.0&request=GetMap&layers=MWT:road_network&bbox=11.5,-29.0,25.5,-16.5&width=768&height=768&srs=EPSG:4326&format=application/openlayers",
            "attribution": "Ministry of Works",
            "name": "Road Network",
            "type": "Namibia"
        },
        "MWT - Railway Network": {
            "url": "https://digitalnamibia.nsa.org.na/geoserver/MWT/wms?service=WMS&version=1.1.0&request=GetMap&layers=MWT:railway_network&bbox=11.5,-29.0,25.5,-16.5&width=768&height=768&srs=EPSG:4326&format=application/openlayers",
            "attribution": "Ministry of Works",
            "name": "Railway Network",
            "type": "Namibia"
        },
        "MWT - Ports and Harbours": {
            "url": "https://digitalnamibia.nsa.org.na/geoserver/MWT/wms?service=WMS&version=1.1.0&request=GetMap&layers=MWT:ports&bbox=11.5,-29.0,25.5,-16.5&width=768&height=768&srs=EPSG:4326&format=application/openlayers",
            "attribution": "Ministry of Works",
            "name": "Ports and Harbours",
            "type": "Namibia"
        },
        "MWT - Airports": {
            "url": "https://digitalnamibia.nsa.org.na/geoserver/MWT/wms?service=WMS&version=1.1.0&request=GetMap&layers=MWT:airports&bbox=11.5,-29.0,25.5,-16.5&width=768&height=768&srs=EPSG:4326&format=application/openlayers",
            "attribution": "Ministry of Works",
            "name": "Airports",
            "type": "Namibia"
        },
        
        # Ministry of Health and Social Services
        "MHSS - Health Facilities": {
            "url": "https://digitalnamibia.nsa.org.na/geoserver/MHSS/wms?service=WMS&version=1.1.0&request=GetMap&layers=MHSS:health_facilities&bbox=11.5,-29.0,25.5,-16.5&width=768&height=768&srs=EPSG:4326&format=application/openlayers",
            "attribution": "Ministry of Health",
            "name": "Health Facilities",
            "type": "Namibia"
        },
        "MHSS - Health Districts": {
            "url": "https://digitalnamibia.nsa.org.na/geoserver/MHSS/wms?service=WMS&version=1.1.0&request=GetMap&layers=MHSS:health_districts&bbox=11.5,-29.0,25.5,-16.5&width=768&height=768&srs=EPSG:4326&format=application/openlayers",
            "attribution": "Ministry of Health",
            "name": "Health Districts",
            "type": "Namibia"
        },
        
        # Ministry of Education, Arts and Culture
        "MEAC - Schools": {
            "url": "https://digitalnamibia.nsa.org.na/geoserver/MEAC/wms?service=WMS&version=1.1.0&request=GetMap&layers=MEAC:schools&bbox=11.5,-29.0,25.5,-16.5&width=768&height=768&srs=EPSG:4326&format=application/openlayers",
            "attribution": "Ministry of Education",
            "name": "Schools",
            "type": "Namibia"
        },
        "MEAC - Education Regions": {
            "url": "https://digitalnamibia.nsa.org.na/geoserver/MEAC/wms?service=WMS&version=1.1.0&request=GetMap&layers=MEAC:education_regions&bbox=11.5,-29.0,25.5,-16.5&width=768&height=768&srs=EPSG:4326&format=application/openlayers",
            "attribution": "Ministry of Education",
            "name": "Education Regions",
            "type": "Namibia"
        },
        
        # Namibia Water Corporation
        "NamWater - Dams": {
            "url": "https://digitalnamibia.nsa.org.na/geoserver/NamWater/wms?service=WMS&version=1.1.0&request=GetMap&layers=NamWater:dams&bbox=11.5,-29.0,25.5,-16.5&width=768&height=768&srs=EPSG:4326&format=application/openlayers",
            "attribution": "NamWater",
            "name": "Dams",
            "type": "Namibia"
        },
        "NamWater - Water Pipelines": {
            "url": "https://digitalnamibia.nsa.org.na/geoserver/NamWater/wms?service=WMS&version=1.1.0&request=GetMap&layers=NamWater:water_pipelines&bbox=11.5,-29.0,25.5,-16.5&width=768&height=768&srs=EPSG:4326&format=application/openlayers",
            "attribution": "NamWater",
            "name": "Water Pipelines",
            "type": "Namibia"
        },
        "NamWater - Boreholes": {
            "url": "https://digitalnamibia.nsa.org.na/geoserver/NamWater/wms?service=WMS&version=1.1.0&request=GetMap&layers=NamWater:boreholes&bbox=11.5,-29.0,25.5,-16.5&width=768&height=768&srs=EPSG:4326&format=application/openlayers",
            "attribution": "NamWater",
            "name": "Boreholes",
            "type": "Namibia"
        },
        
        # Namibia Electricity Control Board
        "NECB - Power Lines": {
            "url": "https://digitalnamibia.nsa.org.na/geoserver/NECB/wms?service=WMS&version=1.1.0&request=GetMap&layers=NECB:power_lines&bbox=11.5,-29.0,25.5,-16.5&width=768&height=768&srs=EPSG:4326&format=application/openlayers",
            "attribution": "NECB",
            "name": "Power Lines",
            "type": "Namibia"
        },
        "NECB - Substations": {
            "url": "https://digitalnamibia.nsa.org.na/geoserver/NECB/wms?service=WMS&version=1.1.0&request=GetMap&layers=NECB:substations&bbox=11.5,-29.0,25.5,-16.5&width=768&height=768&srs=EPSG:4326&format=application/openlayers",
            "attribution": "NECB",
            "name": "Substations",
            "type": "Namibia"
        },
        
        # Namibia Statistics Agency - Census WMS
        "NSA - Constituencies 2014": {
            "url": "https://digitalnamibia.nsa.org.na/geoserver/NSA/wms?service=WMS&version=1.1.0&request=GetMap&layers=NSA:constituencies_2014&bbox=11.5,-29.0,25.5,-16.5&width=768&height=768&srs=EPSG:4326&format=application/openlayers",
            "attribution": "Namibia Statistics Agency",
            "name": "Constituencies 2014",
            "type": "Namibia"
        },
        "NSA - Regions 2012": {
            "url": "https://digitalnamibia.nsa.org.na/geoserver/NSA/wms?service=WMS&version=1.1.0&request=GetMap&layers=NSA:regions_2012&bbox=11.5,-29.0,25.5,-16.5&width=768&height=768&srs=EPSG:4326&format=application/openlayers",
            "attribution": "Namibia Statistics Agency",
            "name": "Regions 2012",
            "type": "Namibia"
        },
        "NSA - Settlements 2011": {
            "url": "https://digitalnamibia.nsa.org.na/geoserver/NSA/wms?service=WMS&version=1.1.0&request=GetMap&layers=NSA:settlements_2011&bbox=11.5,-29.0,25.5,-16.5&width=768&height=768&srs=EPSG:4326&format=application/openlayers",
            "attribution": "Namibia Statistics Agency",
            "name": "Settlements 2011",
            "type": "Namibia"
        },
        
        # Namibia Ports Authority
        "NamPort - Port Infrastructure": {
            "url": "https://digitalnamibia.nsa.org.na/geoserver/NamPort/wms?service=WMS&version=1.1.0&request=GetMap&layers=NamPort:port_infrastructure&bbox=11.5,-29.0,25.5,-16.5&width=768&height=768&srs=EPSG:4326&format=application/openlayers",
            "attribution": "NamPort",
            "name": "Port Infrastructure",
            "type": "Namibia"
        },
        
        # Namibia Civil Aviation Authority
        "NCAA - Flight Routes": {
            "url": "https://digitalnamibia.nsa.org.na/geoserver/NCAA/wms?service=WMS&version=1.1.0&request=GetMap&layers=NCAA:flight_routes&bbox=11.5,-29.0,25.5,-16.5&width=768&height=768&srs=EPSG:4326&format=application/openlayers",
            "attribution": "NCAA",
            "name": "Flight Routes",
            "type": "Namibia"
        },
        "NCAA - Restricted Airspace": {
            "url": "https://digitalnamibia.nsa.org.na/geoserver/NCAA/wms?service=WMS&version=1.1.0&request=GetMap&layers=NCAA:restricted_airspace&bbox=11.5,-29.0,25.5,-16.5&width=768&height=768&srs=EPSG:4326&format=application/openlayers",
            "attribution": "NCAA",
            "name": "Restricted Airspace",
            "type": "Namibia"
        },
        
        # Additional Local Basemaps
        "Namibia - OpenStreetMap (Local)": {
            "url": "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
            "attribution": "OpenStreetMap Namibia",
            "name": "OSM Namibia",
            "type": "General"
        },
        "Namibia - Satellite (ESRI)": {
            "url": "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
            "attribution": "ESRI, DigitalGlobe",
            "name": "ESRI Satellite",
            "type": "Satellite"
        },
        "Namibia - Topographic (ESRI)": {
            "url": "https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}",
            "attribution": "ESRI",
            "name": "ESRI Topographic",
            "type": "Topographic"
        },
        "Namibia - Terrain": {
            "url": "https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png",
            "attribution": "OpenTopoMap",
            "name": "OpenTopoMap",
            "type": "Terrain"
        }
    }
    
    return namibia_basemaps


def get_namibia_xyz_services():
    """Create a formatted list of Namibia services for selection"""
    namibia_basemaps = get_namibia_basemaps()
    
    formatted_services = []
    for key, value in namibia_basemaps.items():
        formatted_services.append({
            "name": key,
            "url": value["url"],
            "attribution": value["attribution"],
            "type": value.get("type", "Namibia")
        })
    
    return formatted_services


def search_namibia_services(keyword, services):
    """Search through Namibia services for matching keywords"""
    if not keyword:
        return []
    
    keyword = keyword.lower()
    results = []
    
    for service in services:
        if (keyword in service["name"].lower() or 
            keyword in service["attribution"].lower() or
            keyword in service.get("type", "").lower()):
            results.append(service["name"])
    
    return results


def app():
    st.title(" Search Basemaps - Namibia Focus")
    st.markdown(
        """
    This app allows you to search and load basemaps from **xyzservices** (1000+ global basemaps), 
    **Quick Map Services (QMS)**, and **NSDI Digital Namibia** with data from various Namibian 
    ministries and agencies. Find the perfect basemap for your analysis with just a few clicks.
    
    **Available Namibian Data Sources:**
    - **NSDI Digital Namibia** - National Spatial Data Infrastructure
    - **Namibia Statistics Agency (NSA)** - Census and demographic data
    -  **Ministry of Agriculture** - Agricultural zones, irrigation schemes
    -  **Ministry of Mines and Energy** - Geology, mining licenses
    -  **Ministry of Environment** - National parks, conservancies
    -  **Ministry of Lands** - Land tenure, resettlement farms
    -  **Ministry of Works** - Roads, railways, airports
    -  **NamWater** - Dams, pipelines, boreholes
    -   **NECB** - Power infrastructure
    -  **Ministry of Health** - Health facilities
    -  **Ministry of Education** - Schools
    """
    )

    with st.expander("📹 See demo"):
        st.image("https://i.imgur.com/0SkUhZh.gif")

    # Load Namibia services
    namibia_services = get_namibia_xyz_services()
    namibia_basemaps = get_namibia_basemaps()

    row1_col1, row1_col2 = st.columns([3, 1])
    width = 800
    height = 600
    tiles = None

    with row1_col2:
        st.subheader("Search Options")
        
        search_scope = st.radio(
            "Search in:",
            ["All Sources", "Global Only", "Namibia Only"],
            index=2  # Default to Namibia Only
        )
        
        search_qms = st.checkbox("Include Quick Map Services (QMS)", value=False)
        
        # Category filter for Namibia data
        if search_scope in ["All Sources", "Namibia Only"]:
            namibia_categories = [
                "All Categories",
                "Base Maps",
                "Administrative Boundaries",
                "Agriculture",
                "Mines & Energy",
                "Environment & Tourism",
                "Infrastructure",
                "Health",
                "Education",
                "Water Resources",
                "Transport",
                "Census Data"
            ]
            selected_category = st.selectbox("Filter by category:", namibia_categories)
        else:
            selected_category = "All Categories"
        
        keyword = st.text_input(" Enter keyword to search (e.g., 'health', 'roads', 'population') and press Enter:", 
                               placeholder="e.g., schools, mines, parks")
        
        empty = st.empty()

        if keyword:
            options = []
            
            # Search in global xyzservices
            if search_scope in ["All Sources", "Global Only"]:
                try:
                    global_options = leafmap.search_xyz_services(keyword=keyword)
                    options.extend(global_options)
                except:
                    pass
            
            # Search in QMS
            if search_qms and search_scope in ["All Sources", "Global Only"]:
                try:
                    qms = leafmap.search_qms(keyword=keyword)
                    if qms is not None:
                        options.extend(qms)
                except:
                    pass
            
            # Search in Namibia services
            if search_scope in ["All Sources", "Namibia Only"]:
                namibia_results = search_namibia_services(keyword, namibia_services)
                
                # Apply category filter if needed
                if selected_category != "All Categories":
                    filtered_results = []
                    category_map = {
                        "Base Maps": ["Satellite", "Topographic", "Terrain", "Imagery"],
                        "Administrative Boundaries": ["Boundaries", "Regions", "Constituencies"],
                        "Agriculture": ["Agriculture", "Irrigation", "Agricultural"],
                        "Mines & Energy": ["Mines", "Mining", "Geological", "Petroleum", "Power"],
                        "Environment & Tourism": ["Parks", "Conservancies", "Forest", "Environment"],
                        "Infrastructure": ["Road", "Railway", "Airport", "Port", "Infrastructure"],
                        "Health": ["Health", "Hospital", "Clinic"],
                        "Education": ["School", "Education"],
                        "Water Resources": ["Dam", "Water", "Borehole", "Pipeline"],
                        "Transport": ["Road", "Railway", "Airport", "Port", "Flight"],
                        "Census Data": ["Census", "Population", "Settlement"]
                    }
                    
                    for result in namibia_results:
                        result_lower = result.lower()
                        for cat_key, cat_terms in category_map.items():
                            if selected_category == cat_key:
                                if any(term.lower() in result_lower for term in cat_terms):
                                    filtered_results.append(result)
                    
                    namibia_results = filtered_results
                
                options.extend(namibia_results)
            
            # Remove duplicates while preserving order
            seen = set()
            options = [x for x in options if not (x in seen or seen.add(x))]
            
            if options:
                tiles = empty.multiselect(
                    f"Select basemaps to add to the map ({len(options)} found):", 
                    options,
                    default=options[0] if len(options) > 0 else None
                )
            else:
                st.warning("No basemaps found. Try different keywords.")
        
        # Quick add buttons for common Namibia basemaps
        st.subheader("🇳🇦 Quick Add Namibia Basemaps")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("NSDI Satellite"):
                tiles = ["NSDI Digital Namibia - Satellite"]
            if st.button("National Parks"):
                tiles = ["MEFT - National Parks"]
            if st.button(" Health Facilities"):
                tiles = ["MHSS - Health Facilities"]
            if st.button(" Road Network"):
                tiles = ["MWT - National Road Network"]
        
        with col2:
            if st.button(" NSDI Topographic"):
                tiles = ["NSDI Digital Namibia - Topographic"]
            if st.button(" Mining Licenses"):
                tiles = ["MME - Mining Licenses"]
            if st.button(" Schools"):
                tiles = ["MEAC - Schools"]
            if st.button(" Dams"):
                tiles = ["NamWater - Dams"]

        with row1_col1:
            m = leafmap.Map(center=[-22.0, 17.0], zoom=5)  # Centered on Namibia
            
            # Add selected tiles
            if tiles is not None:
                for tile in tiles:
                    try:
                        # Check if it's a Namibia service
                        if tile in namibia_basemaps:
                            basemap = namibia_basemaps[tile]
                            m.add_tile_layer(
                                url=basemap["url"],
                                name=basemap["name"],
                                attribution=basemap["attribution"]
                            )
                            st.success(f"Added: {tile}")
                        else:
                            # Try to add as xyzservice
                            m.add_xyz_service(tile)
                            st.success(f" Added: {tile}")
                    except Exception as e:
                        st.error(f"Failed to add {tile}: {str(e)}")
            
            # Add region boundaries as reference (optional)
            add_boundaries = st.checkbox("Show Namibia region boundaries", value=False)
            if add_boundaries:
                try:
                    # Add a simple boundary overlay (you can replace with actual GeoJSON)
                    bounds = [[11.5, -29.0], [25.5, -16.5]]
                    m.add_rect(
                        bounds, 
                        outline_color="red",
                        fill_color=None,
                        layer_name="Namibia Extent"
                    )
                except:
                    pass
            
            m.to_streamlit(height=height)
    
    # Display information about selected layers
    if tiles:
        with st.expander("Selected Layers Information"):
            for tile in tiles:
                if tile in namibia_basemaps:
                    info = namibia_basemaps[tile]
                    st.markdown(f"**{tile}**")
                    st.markdown(f"- Source: {info['attribution']}")
                    st.markdown(f"- Type: {info.get('type', 'Namibia')}")
                    st.markdown("---")
    
    # Data sources footer
    st.markdown("---")
    st.markdown(
        """
        **Data Sources:**
        - **NSDI Digital Namibia** - National geospatial data infrastructure
        - **Namibia Statistics Agency** - Census and demographic boundaries
        - **Various Namibian Ministries** - Sector-specific geospatial data
        - **xyzservices** - Global basemap collection
        - **Quick Map Services (QMS)** - Community-contributed basemaps
        
        *Note: Some services may require internet access and proper authentication. 
        For issues accessing NSDI services, contact the Namibia Statistics Agency.*
        """
    )


app()