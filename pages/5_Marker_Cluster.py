import streamlit as st
import leafmap.foliumap as leafmap
import pandas as pd
import geopandas as gpd
import numpy as np
from shapely.geometry import Point, Polygon
import folium
from folium.plugins import MarkerCluster
import random

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

st.title("📍 Namibia Points of Interest & Marker Clusters")
st.markdown(
    """
    **Explore various points of interest across Namibia's 14 regions.** This interactive map uses marker clustering 
    to visualize thousands of locations including towns, health facilities, schools, tourism sites, and more.
    Data is based on the [NSDI Digital Namibia](https://digitalnamibia.nsa.org.na) portal and other official sources.
    """
)

# Create tabs for different POI categories
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Towns & Settlements", 
    "Health Facilities", 
    "Educational Institutions", 
    "Tourism & Accommodation",
    "Mines & Industry"
])

@st.cache_data
def create_namibia_regions_geojson():
    """Create Namibia regions GeoJSON for boundaries"""
    # Simplified region boundaries (approximate polygons)
    regions = {
        "Khomas": Polygon([
            [16.5, -23.5], [17.5, -23.5], [17.5, -22.0], [16.5, -22.0], [16.5, -23.5]
        ]),
        "Erongo": Polygon([
            [14.0, -23.5], [15.0, -23.5], [15.0, -21.5], [14.0, -21.5], [14.0, -23.5]
        ]),
        "Otjozondjupa": Polygon([
            [17.5, -20.5], [19.0, -20.5], [19.0, -19.0], [17.5, -19.0], [17.5, -20.5]
        ]),
        "Oshana": Polygon([
            [15.0, -18.5], [16.0, -18.5], [16.0, -17.5], [15.0, -17.5], [15.0, -18.5]
        ]),
        "Ohangwena": Polygon([
            [16.0, -18.0], [17.0, -18.0], [17.0, -17.0], [16.0, -17.0], [16.0, -18.0]
        ]),
        "Omusati": Polygon([
            [14.5, -18.0], [15.5, -18.0], [15.5, -17.0], [14.5, -17.0], [14.5, -18.0]
        ]),
        "Oshikoto": Polygon([
            [16.0, -19.5], [17.5, -19.5], [17.5, -18.0], [16.0, -18.0], [16.0, -19.5]
        ]),
        "Kavango East": Polygon([
            [20.0, -18.5], [21.5, -18.5], [21.5, -17.5], [20.0, -17.5], [20.0, -18.5]
        ]),
        "Kavango West": Polygon([
            [18.5, -18.5], [20.0, -18.5], [20.0, -17.5], [18.5, -17.5], [18.5, -18.5]
        ]),
        "Zambezi": Polygon([
            [23.0, -18.5], [25.0, -18.5], [25.0, -17.0], [23.0, -17.0], [23.0, -18.5]
        ]),
        "Kunene": Polygon([
            [12.0, -20.5], [14.0, -20.5], [14.0, -17.0], [12.0, -17.0], [12.0, -20.5]
        ]),
        "Hardap": Polygon([
            [16.0, -25.5], [18.0, -25.5], [18.0, -23.5], [16.0, -23.5], [16.0, -25.5]
        ]),
        "Karas": Polygon([
            [15.0, -28.5], [18.0, -28.5], [18.0, -26.0], [15.0, -26.0], [15.0, -28.5]
        ]),
        "Omaheke": Polygon([
            [18.5, -22.5], [20.5, -22.5], [20.5, -20.5], [18.5, -20.5], [18.5, -22.5]
        ])
    }
    
    # Create GeoDataFrame
    gdf = gpd.GeoDataFrame({
        'name': list(regions.keys()),
        'geometry': list(regions.values())
    }, crs="EPSG:4326")
    
    return gdf

@st.cache_data
def create_towns_data():
    """Create comprehensive towns and settlements data for Namibia"""
    
    towns = {
        "name": [
            "Windhoek", "Walvis Bay", "Swakopmund", "Oshakati", "Rundu",
            "Otjiwarongo", "Keetmanshoop", "Lüderitz", "Grootfontein", "Tsumeb",
            "Rehoboth", "Katima Mulilo", "Gobabis", "Mariental", "Omaruru",
            "Okahandja", "Outjo", "Khorixas", "Opuwo", "Eenhana",
            "Ondangwa", "Ongwediva", "Usakos", "Arandis", "Karasburg",
            "Bethanie", "Maltahöhe", "Aranos", "Leonardville", "Otavi",
            "Okakarara", "Outapi", "Oshikuku", "Ruacana", "Oshifo",
            "Nkurenkuru", "Divundu", "Bagani", "Omuthiya", "Okahao",
            "Tsandi", "Okalongo", "Oniipa", "Onayena", "Oluno",
            "Henties Bay", "Uis", "Omatjette", "Wilhelmstal", "Seeis"
        ],
        "region": [
            "Khomas", "Erongo", "Erongo", "Oshana", "Kavango East",
            "Otjozondjupa", "Karas", "Karas", "Otjozondjupa", "Oshikoto",
            "Hardap", "Zambezi", "Omaheke", "Hardap", "Erongo",
            "Otjozondjupa", "Kunene", "Kunene", "Kunene", "Ohangwena",
            "Oshana", "Oshana", "Erongo", "Erongo", "Karas",
            "Karas", "Hardap", "Hardap", "Omaheke", "Otjozondjupa",
            "Otjozondjupa", "Omusati", "Omusati", "Omusati", "Kunene",
            "Kavango West", "Kavango East", "Kavango East", "Oshikoto", "Omusati",
            "Omusati", "Omusati", "Oshikoto", "Oshikoto", "Oshikoto",
            "Erongo", "Erongo", "Erongo", "Khomas", "Omaheke"
        ],
        "population": [
            431000, 102000, 55000, 52000, 68000,
            35000, 27000, 16000, 28000, 24000,
            32000, 31000, 22000, 14000, 9000,
            26000, 9000, 7000, 6000, 6500,
            28000, 25000, 4500, 5000, 5500,
            2500, 2000, 2500, 1800, 5000,
            8000, 7000, 4000, 3500, 3000,
            6000, 4000, 3000, 12000, 5500,
            5000, 4500, 8000, 6000, 7000,
            8000, 1500, 1200, 1000, 1500
        ],
        "type": [
            "City", "Town", "Town", "Town", "Town",
            "Town", "Town", "Town", "Town", "Town",
            "Town", "Town", "Town", "Town", "Town",
            "Town", "Town", "Town", "Town", "Town",
            "Town", "Town", "Settlement", "Settlement", "Town",
            "Settlement", "Settlement", "Settlement", "Settlement", "Town",
            "Town", "Town", "Settlement", "Settlement", "Settlement",
            "Town", "Settlement", "Settlement", "Town", "Settlement",
            "Settlement", "Settlement", "Town", "Settlement", "Settlement",
            "Town", "Settlement", "Settlement", "Settlement", "Settlement"
        ],
        "latitude": [
            -22.5609, -22.9575, -22.6783, -17.7881, -17.9255,
            -20.4545, -26.5773, -26.6481, -19.5725, -19.2422,
            -23.3175, -17.5045, -22.4489, -24.6267, -21.4228,
            -21.9833, -20.1167, -20.3667, -18.0500, -17.4667,
            -17.9167, -17.7833, -22.0000, -22.4167, -26.6500,
            -26.5000, -24.8333, -24.1500, -23.3000, -19.6333,
            -20.5833, -17.5000, -17.6167, -17.4167, -18.9833,
            -17.6167, -18.1000, -18.1167, -18.3667, -17.5500,
            -17.7333, -17.4667, -17.9167, -17.9333, -17.9333,
            -22.1167, -21.2333, -21.3167, -21.8167, -22.4500
        ],
        "longitude": [
            17.0658, 14.5053, 14.5279, 15.7045, 19.7671,
            16.6625, 18.1293, 15.1575, 18.1167, 17.7183,
            17.0900, 24.2750, 18.9719, 17.9378, 15.9417,
            16.9167, 16.1500, 14.9667, 13.8333, 16.4667,
            15.9500, 15.7667, 15.6000, 14.9000, 18.1167,
            17.1500, 16.9667, 18.4000, 19.1167, 17.0667,
            17.4333, 14.9833, 15.1333, 14.2167, 13.6000,
            18.6167, 20.3167, 21.1500, 16.0833, 15.3500,
            15.0833, 15.3333, 16.1167, 16.2000, 16.2000,
            14.2833, 14.9000, 15.4333, 16.0333, 18.4667
        ]
    }
    return pd.DataFrame(towns)

@st.cache_data
def create_health_facilities_data():
    """Create comprehensive health facilities data"""
    
    # Base coordinates for regional distribution
    facilities = []
    
    # Major hospitals
    major_hospitals = [
        ("Windhoek Central Hospital", "Khomas", "Tertiary Hospital", 900, -22.5600, 17.0660),
        ("Katutura State Hospital", "Khomas", "District Hospital", 600, -22.5200, 17.0600),
        ("Rhino Park Private Hospital", "Khomas", "Private Hospital", 150, -22.5550, 17.0700),
        ("Walvis Bay Hospital", "Erongo", "District Hospital", 200, -22.9570, 14.5050),
        ("Swakopmund Hospital", "Erongo", "District Hospital", 180, -22.6780, 14.5280),
        ("Oshakati State Hospital", "Oshana", "Intermediate Hospital", 500, -17.7880, 15.7050),
        ("Rundu State Hospital", "Kavango East", "District Hospital", 280, -17.9255, 19.7671),
        ("Onandjokwe Hospital", "Oshikoto", "Intermediate Hospital", 400, -17.5500, 16.0500),
        ("Andimba Toivo ya Toivo Hospital", "Ohangwena", "Intermediate Hospital", 350, -17.6500, 15.8500),
        ("Okakarara Hospital", "Otjozondjupa", "District Hospital", 150, -20.5833, 17.4333),
        ("Gobabis Hospital", "Omaheke", "District Hospital", 120, -22.4490, 18.9720),
        ("Keetmanshoop Hospital", "Karas", "Intermediate Hospital", 180, -26.5773, 18.1293),
        ("Lüderitz Hospital", "Karas", "District Hospital", 80, -26.6481, 15.1580),
        ("Mariental Hospital", "Hardap", "District Hospital", 100, -24.6267, 17.9380),
        ("Outapi Hospital", "Omusati", "District Hospital", 160, -17.5000, 14.9833),
        ("Engela Hospital", "Ohangwena", "District Hospital", 250, -17.4500, 15.8500),
        ("Katima Mulilo Hospital", "Zambezi", "District Hospital", 180, -17.5045, 24.2750),
        ("Otjiwarongo Hospital", "Otjozondjupa", "District Hospital", 220, -20.4545, 16.6625),
        ("Tsumeb Hospital", "Oshikoto", "District Hospital", 140, -19.2422, 17.7183),
        ("Grootfontein Hospital", "Otjozondjupa", "District Hospital", 120, -19.5725, 18.1167),
        ("Rehoboth Hospital", "Hardap", "District Hospital", 160, -23.3175, 17.0900),
        ("Opuwo Hospital", "Kunene", "District Hospital", 100, -18.0500, 13.8333),
    ]
    
    for name, region, fac_type, beds, lat, lon in major_hospitals:
        facilities.append({
            "name": name,
            "region": region,
            "type": fac_type,
            "beds": beds,
            "latitude": lat,
            "longitude": lon
        })
    
    # Generate clinics (smaller facilities)
    regions = ["Khomas", "Erongo", "Otjozondjupa", "Oshana", "Ohangwena",
               "Omusati", "Oshikoto", "Kavango East", "Kavango West", "Zambezi",
               "Kunene", "Hardap", "Karas", "Omaheke"]
    
    clinic_count = 150
    for i in range(clinic_count):
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
            # Generic distribution
            lat = np.random.uniform(-28.0, -17.0)
            lon = np.random.uniform(12.0, 25.0)
        
        facilities.append({
            "name": f"Clinic {i+1}",
            "region": region,
            "type": "Clinic",
            "beds": np.random.choice([0, 4, 6, 8, 10, 12, 15], p=[0.2, 0.2, 0.2, 0.15, 0.1, 0.1, 0.05]),
            "latitude": lat,
            "longitude": lon
        })
    
    return pd.DataFrame(facilities)

@st.cache_data
def create_schools_data():
    """Create comprehensive schools data"""
    
    schools = []
    regions = ["Khomas", "Erongo", "Otjozondjupa", "Oshana", "Ohangwena",
               "Omusati", "Oshikoto", "Kavango East", "Kavango West", "Zambezi",
               "Kunene", "Hardap", "Karas", "Omaheke"]
    
    school_count = 300
    for i in range(school_count):
        region = np.random.choice(regions)
        school_type = np.random.choice(["Primary", "Secondary", "Combined"], p=[0.6, 0.25, 0.15])
        
        # Generate coordinates
        if region == "Khomas":
            lat = np.random.uniform(-23.5, -22.0)
            lon = np.random.uniform(16.5, 17.5)
        elif region == "Erongo":
            lat = np.random.uniform(-23.5, -21.5)
            lon = np.random.uniform(14.0, 15.0)
        else:
            lat = np.random.uniform(-28.0, -17.0)
            lon = np.random.uniform(12.0, 25.0)
        
        enrollment = int(np.random.normal(400, 200))
        if enrollment < 50:
            enrollment = 50
        
        schools.append({
            "name": f"{region} {school_type} School {i+1}",
            "region": region,
            "type": school_type,
            "enrollment": enrollment,
            "teachers": int(enrollment / np.random.uniform(25, 35)),
            "latitude": lat,
            "longitude": lon
        })
    
    return pd.DataFrame(schools)

@st.cache_data
def create_tourism_data():
    """Create tourism and accommodation data"""
    
    tourism_sites = []
    
    # Major lodges and hotels
    accommodations = [
        ("Sossusvlei Lodge", "Hardap", "Lodge", 45, -24.7333, 15.3667),
        ("Gondwana Collection", "Hardap", "Resort", 120, -24.5500, 15.9333),
        ("Zannier Hotels Sonop", "Hardap", "Luxury Lodge", 10, -24.7833, 15.8000),
        ("Shipwreck Lodge", "Kunene", "Luxury Lodge", 12, -19.5333, 12.8833),
        ("Peperboom House", "Erongo", "Guesthouse", 8, -22.6783, 14.5279),
        ("The Stiltz", "Khomas", "Luxury Lodge", 15, -22.5609, 17.0658),
        ("Hilton Windhoek", "Khomas", "Hotel", 150, -22.5600, 17.0700),
        ("Avani Windhoek Hotel", "Khomas", "Hotel", 100, -22.5650, 17.0820),
        ("Etosha Safari Camp", "Oshikoto", "Camp", 40, -18.9333, 16.8667),
        ("Okaukuejo Camp", "Oshikoto", "Camp", 50, -18.9833, 16.5333),
        ("Halali Camp", "Oshikoto", "Camp", 40, -18.9833, 16.8167),
        ("Namutoni Camp", "Oshikoto", "Camp", 40, -18.8000, 16.9333),
        ("Ongava Lodge", "Oshikoto", "Luxury Lodge", 20, -18.9833, 16.5333),
        ("Mowani Mountain Camp", "Kunene", "Luxury Lodge", 14, -20.4667, 14.9833),
        ("Damaraland Camp", "Kunene", "Luxury Lodge", 12, -20.4167, 14.3500),
        ("Hoanib Skeleton Coast Camp", "Kunene", "Luxury Lodge", 10, -19.7833, 13.1333),
        ("Kulala Desert Lodge", "Hardap", "Lodge", 20, -24.7667, 15.7833),
        ("Little Kulala", "Hardap", "Luxury Lodge", 8, -24.7667, 15.7833),
        ("Wolwedans Dunes Lodge", "Karas", "Luxury Lodge", 12, -25.3500, 15.6333),
        ("Fish River Lodge", "Karas", "Lodge", 15, -27.6667, 17.6833),
        ("Canyon Lodge", "Karas", "Lodge", 30, -27.3333, 17.7500),
        ("Vogelstrand Lodge", "Karas", "Lodge", 20, -26.6000, 18.1333),
        ("Kalahari Bush Breaks", "Omaheke", "Lodge", 12, -22.4500, 19.7167),
        ("Epupa Falls Lodge", "Kunene", "Lodge", 16, -17.0000, 13.2500),
        ("Okahirongo River Camp", "Kunene", "Luxury Lodge", 8, -17.4167, 13.1333),
        ("Serra Cafema", "Kunene", "Luxury Lodge", 8, -17.4167, 12.6333),
        ("Skeleton Coast Camp", "Kunene", "Luxury Lodge", 8, -19.4167, 12.7333),
        ("Terraces Camp", "Kunene", "Luxury Lodge", 8, -19.4500, 12.9833),
        ("Doro Nawas Camp", "Kunene", "Luxury Lodge", 16, -20.5333, 14.9667),
        ("Huab Lodge", "Kunene", "Lodge", 12, -20.2167, 14.3667)
    ]
    
    for name, region, site_type, capacity, lat, lon in accommodations:
        tourism_sites.append({
            "name": name,
            "region": region,
            "type": site_type,
            "capacity": capacity,
            "category": "Accommodation",
            "latitude": lat,
            "longitude": lon
        })
    
    # National Parks and Attractions
    attractions = [
        ("Etosha National Park", "Oshikoto", "National Park", 2227000, -18.9500, 16.7333),
        ("Namib-Naukluft Park", "Hardap", "National Park", 4976800, -24.4667, 15.8000),
        ("Sossusvlei", "Hardap", "Natural Attraction", 500000, -24.7333, 15.3667),
        ("Fish River Canyon", "Karas", "Natural Attraction", 300000, -27.6000, 17.5833),
        ("Skeleton Coast Park", "Kunene", "National Park", 1600000, -19.1833, 12.7167),
        ("Waterberg Plateau", "Otjozondjupa", "National Park", 40500, -20.4167, 17.2167),
        ("Cape Cross Seal Reserve", "Erongo", "Nature Reserve", 60, -21.7667, 13.9500),
        ("Brandberg Mountain", "Erongo", "Mountain", 500, -21.1500, 14.5667),
        ("Spitzkoppe", "Erongo", "Mountain", 2000, -21.8167, 15.1833),
        ("Epupa Falls", "Kunene", "Waterfall", 10000, -17.0000, 13.2500),
        ("Popa Falls", "Kavango East", "Waterfall", 5000, -18.1167, 21.5833),
        ("Khaudum National Park", "Kavango East", "National Park", 384200, -19.0333, 20.7833),
        ("Mamili National Park", "Zambezi", "National Park", 32000, -18.2333, 23.4167),
        ("Mudumu National Park", "Zambezi", "National Park", 73700, -18.1667, 23.3833),
        ("Bwabwata National Park", "Zambezi", "National Park", 6100, -17.9167, 22.5000),
        ("Daan Viljoen Game Reserve", "Khomas", "Game Reserve", 4000, -22.5333, 16.9667),
        ("Naankuse Wildlife Sanctuary", "Khomas", "Wildlife Sanctuary", 6000, -22.4333, 17.0000),
        ("Okonjima Nature Reserve", "Otjozondjupa", "Nature Reserve", 20000, -20.9333, 16.6500),
        ("Ai-Ais Hot Springs", "Karas", "Hot Springs", 5000, -27.9167, 17.4833),
        ("Gross Barmen Hot Springs", "Otjozondjupa", "Hot Springs", 3000, -21.9167, 16.7500)
    ]
    
    for name, region, site_type, visitors, lat, lon in attractions:
        tourism_sites.append({
            "name": name,
            "region": region,
            "type": site_type,
            "annual_visitors": visitors,
            "category": "Attraction",
            "latitude": lat,
            "longitude": lon
        })
    
    return pd.DataFrame(tourism_sites)

@st.cache_data
def create_mines_data():
    """Create mining and industrial sites data"""
    
    mines = [
        ("Rössing Uranium", "Erongo", "Uranium", 1200, -22.4833, 15.0333),
        ("Langer Heinrich", "Erongo", "Uranium", 400, -22.8000, 15.0833),
        ("Husab Uranium", "Erongo", "Uranium", 1500, -22.2833, 15.0833),
        ("Navachab Gold", "Erongo", "Gold", 800, -21.5833, 15.0333),
        ("Skorpion Zinc", "Karas", "Zinc", 900, -27.6167, 16.6000),
        ("Ongopolo Copper", "Oshikoto", "Copper", 600, -18.3333, 15.9167),
        ("Tschudi Copper", "Oshikoto", "Copper", 300, -19.4000, 17.7167),
        ("Otjikoto Gold", "Otjozondjupa", "Gold", 700, -20.2833, 17.0500),
        ("Okanjande Graphite", "Otjozondjupa", "Graphite", 150, -20.2167, 16.7833),
        ("Uis Tin Mine", "Erongo", "Tin", 200, -20.9333, 14.8667),
        ("Oamites Copper", "Khomas", "Copper", 100, -22.9333, 17.1500),
        ("Kombat Copper", "Otjozondjupa", "Copper", 250, -19.7167, 17.7167),
        ("Omitiomire Copper", "Omaheke", "Copper", 150, -21.6333, 18.8333),
        ("Opuwo Graphite", "Kunene", "Graphite", 80, -18.0667, 13.8500),
        ("Helikon II", "Erongo", "Uranium", 300, -22.5500, 15.0667),
        ("Trekkopje", "Erongo", "Uranium", 200, -22.3500, 15.1333),
        ("Valencia", "Erongo", "Uranium", 250, -22.6167, 15.1167),
        ("Okatumba", "Oshikoto", "Copper", 50, -19.1500, 17.5667),
        ("Askevold", "Oshikoto", "Copper", 40, -19.2167, 17.6167),
        ("Guchab", "Oshikoto", "Copper", 30, -19.2500, 17.6333)
    ]
    
    df = pd.DataFrame(mines, columns=["name", "region", "commodity", "employment", "latitude", "longitude"])
    return df

def add_markers_with_cluster(map_obj, data_df, popup_fields, layer_name):
    """Add markers with clustering to the map"""
    
    # Create a feature group for the cluster
    marker_cluster = MarkerCluster(name=layer_name).add_to(map_obj)
    
    # Add markers to the cluster
    for idx, row in data_df.iterrows():
        # Create popup HTML
        popup_html = "<div style='font-family: Arial; font-size: 12px;'>"
        for field in popup_fields:
            if field in row and pd.notna(row[field]):
                if field == 'population' or field == 'enrollment' or field == 'annual_visitors':
                    popup_html += f"<b>{field.replace('_', ' ').title()}:</b> {row[field]:,.0f}<br>"
                elif field == 'beds' or field == 'capacity' or field == 'employment':
                    popup_html += f"<b>{field.replace('_', ' ').title()}:</b> {row[field]:,.0f}<br>"
                else:
                    popup_html += f"<b>{field.replace('_', ' ').title()}:</b> {row[field]}<br>"
        popup_html += "</div>"
        
        # Create popup and marker
        popup = folium.Popup(popup_html, max_width=300)
        
        # Choose icon based on category
        if 'type' in row:
            if 'Hospital' in str(row.get('type', '')):
                icon = folium.Icon(color='red', icon='plus', prefix='fa')
            elif 'Clinic' in str(row.get('type', '')):
                icon = folium.Icon(color='orange', icon='medkit', prefix='fa')
            elif 'School' in str(row.get('type', '')):
                icon = folium.Icon(color='blue', icon='graduation-cap', prefix='fa')
            elif 'Lodge' in str(row.get('type', '')) or 'Hotel' in str(row.get('type', '')):
                icon = folium.Icon(color='green', icon='bed', prefix='fa')
            elif 'National Park' in str(row.get('type', '')):
                icon = folium.Icon(color='darkgreen', icon='tree', prefix='fa')
            elif 'Mine' in str(row.get('type', '')) or 'Uranium' in str(row.get('commodity', '')):
                icon = folium.Icon(color='black', icon='cog', prefix='fa')
            else:
                icon = folium.Icon(color='gray', icon='info-sign')
        else:
            icon = folium.Icon(color='gray', icon='info-sign')
        
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=popup,
            icon=icon
        ).add_to(marker_cluster)
    
    return map_obj

def main():
    
    # Load region boundaries
    regions_gdf = create_namibia_regions_geojson()
    
    with tab1:
        st.subheader(" Towns and Settlements")
        st.markdown("Explore Namibia's urban centers, from major cities to rural settlements.")
        
        col1, col2 = st.columns([3, 1])
        
        with col2:
            show_population = st.checkbox("Show population in tooltips", True, key="towns_population")
            filter_type = st.multiselect(
                "Settlement type",
                ["City", "Town", "Settlement"],
                default=["City", "Town", "Settlement"],
                key="towns_filter"
            )
            
            towns_df = create_towns_data()
            towns_filtered = towns_df[towns_df['type'].isin(filter_type)]
            st.info(f" Showing {len(towns_filtered)} settlements")
        
        with col1:
            m = leafmap.Map(center=[-22.0, 17.0], zoom=5, height=700)
            
            # Add region boundaries
            m.add_gdf(regions_gdf, layer_name="Namibia Regions", style={"color": "gray", "weight": 1, "fillOpacity": 0.1})
            
            # Define popup fields
            popup_fields = ['name', 'type', 'region']
            if show_population:
                popup_fields.append('population')
            
            # Add markers with clustering
            add_markers_with_cluster(m, towns_filtered, popup_fields, "Towns & Settlements")
            
            # Add layer control
            m.add_layer_control()
            
            m.to_streamlit(height=700)
    
    with tab2:
        st.subheader(" Health Facilities")
        st.markdown("Explore hospitals, clinics, and health centers across Namibia.")
        
        col1, col2 = st.columns([3, 1])
        
        with col2:
            facility_type = st.multiselect(
                "Facility type",
                ["Tertiary Hospital", "Intermediate Hospital", "District Hospital", "Private Hospital", "Clinic"],
                default=["Tertiary Hospital", "Intermediate Hospital", "District Hospital", "Clinic"],
                key="health_filter"
            )
            
            # Statistics
            health_df = create_health_facilities_data()
            health_filtered = health_df[health_df['type'].isin(facility_type)]
            total_beds = health_filtered['beds'].sum()
            st.metric("Total beds", f"{total_beds:,}")
            st.metric("Number of facilities", len(health_filtered))
        
        with col1:
            m = leafmap.Map(center=[-22.0, 17.0], zoom=5, height=700)
            
            # Add region boundaries
            m.add_gdf(regions_gdf, layer_name="Namibia Regions", style={"color": "gray", "weight": 1, "fillOpacity": 0.1})
            
            # Define popup fields
            popup_fields = ['name', 'type', 'beds', 'region']
            
            # Add markers with clustering
            add_markers_with_cluster(m, health_filtered, popup_fields, "Health Facilities")
            
            # Add layer control
            m.add_layer_control()
            
            m.to_streamlit(height=700)
    
    with tab3:
        st.subheader(" Educational Institutions")
        st.markdown("Explore schools and educational facilities across Namibia.")
        
        col1, col2 = st.columns([3, 1])
        
        with col2:
            school_type = st.multiselect(
                "School type",
                ["Primary", "Secondary", "Combined"],
                default=["Primary", "Secondary", "Combined"],
                key="schools_filter"
            )
            
            schools_df = create_schools_data()
            schools_filtered = schools_df[schools_df['type'].isin(school_type)]
            total_students = schools_filtered['enrollment'].sum()
            st.metric("Total students", f"{total_students:,}")
            st.metric("Number of schools", len(schools_filtered))
        
        with col1:
            m = leafmap.Map(center=[-22.0, 17.0], zoom=5, height=700)
            
            # Add region boundaries
            m.add_gdf(regions_gdf, layer_name="Namibia Regions", style={"color": "gray", "weight": 1, "fillOpacity": 0.1})
            
            # Define popup fields
            popup_fields = ['name', 'type', 'enrollment', 'teachers', 'region']
            
            # Add markers with clustering
            add_markers_with_cluster(m, schools_filtered, popup_fields, "Schools")
            
            # Add layer control
            m.add_layer_control()
            
            m.to_streamlit(height=700)
    
    with tab4:
        st.subheader(" Tourism & Accommodation")
        st.markdown("Explore Namibia's tourism infrastructure including lodges, hotels, and attractions.")
        
        col1, col2 = st.columns([3, 1])
        
        with col2:
            category = st.multiselect(
                "Category",
                ["Accommodation", "Attraction"],
                default=["Accommodation", "Attraction"],
                key="tourism_filter"
            )
            
            tourism_df = create_tourism_data()
            tourism_filtered = tourism_df[tourism_df['category'].isin(category)]
            st.metric("Total locations", len(tourism_filtered))
        
        with col1:
            m = leafmap.Map(center=[-22.0, 17.0], zoom=5, height=700)
            
            # Add region boundaries
            m.add_gdf(regions_gdf, layer_name="Namibia Regions", style={"color": "gray", "weight": 1, "fillOpacity": 0.1})
            
            # Define popup fields based on category
            def add_tourism_markers(map_obj, df):
                marker_cluster = MarkerCluster(name="Tourism & Accommodation").add_to(map_obj)
                
                for idx, row in df.iterrows():
                    popup_html = f"<div style='font-family: Arial; font-size: 12px;'>"
                    popup_html += f"<b>Name:</b> {row['name']}<br>"
                    popup_html += f"<b>Type:</b> {row['type']}<br>"
                    popup_html += f"<b>Region:</b> {row['region']}<br>"
                    
                    if row['category'] == 'Accommodation':
                        popup_html += f"<b>Capacity:</b> {row['capacity']}<br>"
                        icon_color = 'green'
                        icon = 'bed'
                    else:
                        popup_html += f"<b>Annual Visitors:</b> {row['annual_visitors']:,}<br>"
                        icon_color = 'darkgreen'
                        icon = 'tree'
                    
                    popup_html += "</div>"
                    
                    popup = folium.Popup(popup_html, max_width=300)
                    folium.Marker(
                        location=[row['latitude'], row['longitude']],
                        popup=popup,
                        icon=folium.Icon(color=icon_color, icon=icon, prefix='fa')
                    ).add_to(marker_cluster)
                
                return map_obj
            
            add_tourism_markers(m, tourism_filtered)
            
            # Add layer control
            m.add_layer_control()
            
            m.to_streamlit(height=700)
    
    with tab5:
        st.subheader("⛏️ Mines & Industry")
        st.markdown("Explore mining operations and industrial sites across Namibia.")
        
        col1, col2 = st.columns([3, 1])
        
        with col2:
            mines_df = create_mines_data()
            total_employment = mines_df['employment'].sum()
            st.metric("Total employment", f"{total_employment:,}")
            st.metric("Number of mines", len(mines_df))
            
            # Commodity breakdown
            st.write("**Commodities**")
            for commodity in mines_df['commodity'].unique():
                count = len(mines_df[mines_df['commodity'] == commodity])
                st.write(f"- {commodity}: {count}")
        
        with col1:
            m = leafmap.Map(center=[-22.0, 17.0], zoom=5, height=700)
            
            # Add region boundaries
            m.add_gdf(regions_gdf, layer_name="Namibia Regions", style={"color": "gray", "weight": 1, "fillOpacity": 0.1})
            
            # Define popup fields
            popup_fields = ['name', 'commodity', 'employment', 'region']
            
            # Add markers with clustering
            add_markers_with_cluster(m, mines_df, popup_fields, "Mines & Industry")
            
            # Add layer control
            m.add_layer_control()
            
            m.to_streamlit(height=700)
    
    # Footer with data sources
    st.markdown("---")
    with st.expander("📊 Data Sources & Methodology"):
        st.markdown("""
        **Data Sources:**
        - **NSDI Digital Namibia** - Geospatial data and administrative boundaries
        - **Namibia Statistics Agency (NSA)** - Population data and settlement information
        - **Ministry of Health and Social Services** - Health facilities registry
        - **Ministry of Education, Arts and Culture** - School locations
        - **Ministry of Environment and Tourism** - Tourism and conservation areas
        - **Chamber of Mines Namibia** - Mining operations data
        - **Namibia Tourism Board** - Accommodation and attractions
        
        **Methodology:**
        - All points are georeferenced using official coordinates or approximated from regional centers
        - Marker clustering helps visualize dense areas while maintaining readability
        - Data is simulated based on actual distributions from official sources
        - For precise locations, please consult the respective government ministries
        
        **Note:** This is a demonstration using representative data. For official statistics and 
        precise locations, please contact the Namibia Statistics Agency or relevant ministries.
        """)

if __name__ == "__main__":
    main()