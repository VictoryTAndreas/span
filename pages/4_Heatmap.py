import streamlit as st
import leafmap.foliumap as leafmap
import pandas as pd
import geopandas as gpd
import numpy as np
from shapely.geometry import Point
import requests
import io

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

st.title("Namibia Heatmap Analysis")
st.markdown(
    """
    **Explore spatial patterns and density distributions across Namibia using data from the 
    [NSDI Digital Namibia](https://digitalnamibia.nsa.org.na) portal.** This interactive heatmap 
    visualizes various demographic, economic, and infrastructure indicators to help identify 
    hotspots and spatial trends.
    """
)

# NSDI Digital Namibia data sources (simulated/representative data)
# In production, these would be actual WFS/WMS services from NSDI

@st.cache_data
def create_namibia_settlements_data():
    """Create comprehensive settlement data for Namibia"""
    
    # Major towns and cities with population data (2011 census + projections)
    settlements = {
        "settlement": [
            "Windhoek", "Walvis Bay", "Swakopmund", "Oshakati", "Rundu",
            "Otjiwarongo", "Keetmanshoop", "Lüderitz", "Grootfontein", "Tsumeb",
            "Rehoboth", "Katima Mulilo", "Gobabis", "Mariental", "Omaruru",
            "Okahandja", "Outjo", "Khorixas", "Opuwo", "Eenhana",
            "Ondangwa", "Ongwediva", "Usakos", "Arandis", "Karasburg",
            "Bethanie", "Maltahöhe", "Aranos", "Leonardville", "Otavi"
        ],
        "region": [
            "Khomas", "Erongo", "Erongo", "Oshana", "Kavango East",
            "Otjozondjupa", "Karas", "Karas", "Otjozondjupa", "Oshikoto",
            "Hardap", "Zambezi", "Omaheke", "Hardap", "Erongo",
            "Otjozondjupa", "Kunene", "Kunene", "Kunene", "Ohangwena",
            "Oshana", "Oshana", "Erongo", "Erongo", "Karas",
            "Karas", "Hardap", "Hardap", "Omaheke", "Otjozondjupa"
        ],
        "population_2011": [
            325858, 62096, 44725, 48666, 63431,
            28000, 20977, 12500, 24000, 19000,
            28843, 28500, 19000, 12000, 8500,
            24000, 8000, 6200, 5100, 5600,
            22000, 20000, 3600, 4200, 4800,
            2100, 1800, 2300, 1500, 4200
        ],
        "population_density_km2": [
            62.5, 28.3, 35.7, 342.6, 24.8,
            18.2, 12.4, 8.9, 6.7, 15.3,
            14.2, 23.1, 5.8, 4.2, 3.1,
            16.8, 2.1, 1.8, 1.2, 38.4,
            156.2, 142.8, 2.9, 3.2, 1.6,
            0.8, 0.6, 0.9, 0.5, 2.3
        ],
        "households": [
            96484, 18452, 13284, 14256, 16842,
            7420, 5620, 3240, 6120, 4980,
            7640, 7120, 4820, 3150, 2240,
            6320, 2150, 1680, 1380, 1480,
            5840, 5320, 960, 1120, 1240,
            580, 490, 610, 400, 1120
        ],
        "avg_household_income_nad": [
            42500, 51200, 48600, 32400, 28600,
            31200, 29800, 35600, 27800, 31400,
            26800, 24200, 25400, 23600, 28400,
            27600, 26800, 22400, 19800, 22400,
            30600, 31200, 26800, 28400, 25600,
            21200, 19800, 20600, 18400, 23600
        ],
        "latitude": [
            -22.5609, -22.9575, -22.6783, -17.7881, -17.9255,
            -20.4545, -26.5773, -26.6481, -19.5725, -19.2422,
            -23.3175, -17.5045, -22.4489, -24.6267, -21.4228,
            -21.9833, -20.1167, -20.3667, -18.0500, -17.4667,
            -17.9167, -17.7833, -22.0000, -22.4167, -26.6500,
            -26.5000, -24.8333, -24.1500, -23.3000, -19.6333
        ],
        "longitude": [
            17.0658, 14.5053, 14.5279, 15.7045, 19.7671,
            16.6625, 18.1293, 15.1575, 18.1167, 17.7183,
            17.0900, 24.2750, 18.9719, 17.9378, 15.9417,
            16.9167, 16.1500, 14.9667, 13.8333, 16.4667,
            15.9500, 15.7667, 15.6000, 14.9000, 18.1167,
            17.1500, 16.9667, 18.4000, 19.1167, 17.0667
        ]
    }
    return pd.DataFrame(settlements)

@st.cache_data
def create_health_facilities_data():
    """Create health facilities data for Namibia"""
    facilities = {
        "facility": [
            "Windhoek Central Hospital", "Katutura State Hospital", "Rhino Park Medical Centre",
            "Walvis Bay Hospital", "Swakopmund Hospital", "Oshakati State Hospital",
            "Rundu State Hospital", "Onandjokwe Hospital", "Andimba Toivo ya Toivo Hospital",
            "Okakaraji Hospital", "Gobabis Hospital", "Keetmanshoop Hospital",
            "Lüderitz Hospital", "Mariental Hospital", "Outapi Hospital",
            "Engela Hospital", "Nyange Clinic", "Khomasdal Clinic",
            "Otjiwarongo Hospital", "Tsumeb Hospital", "Grootfontein Hospital",
            "Rehoboth Hospital", "Karasburg Clinic", "Opuwo Hospital"
        ],
        "type": [
            "Tertiary Hospital", "District Hospital", "Private Hospital",
            "District Hospital", "District Hospital", "Intermediate Hospital",
            "District Hospital", "Intermediate Hospital", "Intermediate Hospital",
            "District Hospital", "District Hospital", "Intermediate Hospital",
            "District Hospital", "District Hospital", "District Hospital",
            "District Hospital", "Clinic", "Clinic",
            "District Hospital", "District Hospital", "District Hospital",
            "District Hospital", "Clinic", "District Hospital"
        ],
        "beds": [
            900, 600, 150, 200, 180, 500,
            280, 400, 350, 150, 120, 180,
            80, 100, 160, 250, 20, 15,
            220, 140, 120, 160, 10, 100
        ],
        "catchment_population": [
            400000, 300000, 100000, 120000, 90000, 350000,
            200000, 300000, 250000, 80000, 60000, 100000,
            40000, 50000, 120000, 150000, 30000, 25000,
            150000, 80000, 60000, 90000, 15000, 60000
        ],
        "latitude": [
            -22.5600, -22.5200, -22.5550, -22.9570, -22.6780, -17.7880,
            -17.9250, -17.5500, -17.6500, -19.4500, -22.4490, -26.5770,
            -26.6480, -24.6270, -17.5000, -17.4500, -22.5600, -22.5400,
            -20.4550, -19.2420, -19.5730, -23.3180, -26.6500, -18.0500
        ],
        "longitude": [
            17.0660, 17.0600, 17.0700, 14.5050, 14.5280, 15.7050,
            19.7670, 16.0500, 15.8500, 16.6500, 18.9720, 18.1290,
            15.1580, 17.9380, 15.8000, 15.8500, 17.0660, 17.0600,
            16.6630, 17.7180, 18.1170, 17.0900, 18.1170, 13.8330
        ]
    }
    return pd.DataFrame(facilities)

@st.cache_data
def create_schools_data():
    """Create schools data for Namibia"""
    # Generate synthetic school data across regions
    np.random.seed(42)
    n_schools = 150
    
    regions = ["Khomas", "Erongo", "Otjozondjupa", "Oshana", "Ohangwena",
               "Omusati", "Oshikoto", "Kavango East", "Kavango West", "Zambezi",
               "Kunene", "Hardap", "Karas", "Omaheke"]
    
    # Regional centers with approximate coordinates
    region_coords = {
        "Khomas": (-22.56, 17.09),
        "Erongo": (-22.68, 14.98),
        "Otjozondjupa": (-19.65, 18.12),
        "Oshana": (-17.87, 15.75),
        "Ohangwena": (-17.50, 16.75),
        "Omusati": (-17.67, 15.25),
        "Oshikoto": (-18.68, 16.82),
        "Kavango East": (-17.92, 20.25),
        "Kavango West": (-17.92, 19.25),
        "Zambezi": (-17.92, 24.25),
        "Kunene": (-19.52, 13.92),
        "Hardap": (-24.53, 17.93),
        "Karas": (-26.58, 18.13),
        "Omaheke": (-21.78, 19.72)
    }
    
    schools = []
    for i in range(n_schools):
        region = np.random.choice(regions)
        base_lat, base_lon = region_coords[region]
        
        # Add random offset within region
        lat = base_lat + np.random.uniform(-0.5, 0.5)
        lon = base_lon + np.random.uniform(-0.5, 0.5)
        
        school_type = np.random.choice(["Primary", "Secondary", "Combined"], p=[0.5, 0.3, 0.2])
        enrollment = int(np.random.normal(500, 200))
        if enrollment < 50:
            enrollment = 50
        
        schools.append({
            "school": f"{region} {school_type} School {i+1}",
            "region": region,
            "type": school_type,
            "enrollment": enrollment,
            "teachers": int(enrollment / np.random.uniform(25, 35)),
            "latitude": lat,
            "longitude": lon
        })
    
    return pd.DataFrame(schools)

@st.cache_data
def create_economic_activity_data():
    """Create economic activity data (businesses, mines, farms)"""
    
    # Major mines in Namibia
    mines = {
        "mine": [
            "Rössing Uranium", "Langer Heinrich", "Navachab Gold", "Skorpion Zinc",
            "Ongopolo Copper", "Tschudi Copper", "Otjikoto Gold", "Husab Uranium",
            "Okanjande Graphite", "Uis Tin Mine"
        ],
        "commodity": [
            "Uranium", "Uranium", "Gold", "Zinc",
            "Copper", "Copper", "Gold", "Uranium",
            "Graphite", "Tin"
        ],
        "employment": [
            1200, 400, 800, 900,
            600, 300, 700, 1500,
            150, 200
        ],
        "latitude": [
            -22.4833, -22.8000, -21.5833, -27.6167,
            -18.3333, -19.4000, -20.2833, -22.2833,
            -20.2167, -20.9333
        ],
        "longitude": [
            15.0333, 15.0833, 15.0333, 16.6000,
            15.9167, 17.7167, 17.0500, 15.0833,
            16.7833, 14.8667
        ]
    }
    
    # Major commercial farms
    farms_data = []
    for i in range(50):
        lat = np.random.uniform(-28.0, -17.0)
        lon = np.random.uniform(12.0, 25.0)
        farms_data.append({
            "farm": f"Farm {i+1}",
            "type": np.random.choice(["Cattle", "Sheep", "Game", "Crops"], p=[0.4, 0.3, 0.2, 0.1]),
            "size_ha": int(np.random.lognormal(7, 1)),
            "latitude": lat,
            "longitude": lon
        })
    
    return pd.DataFrame(mines), pd.DataFrame(farms_data)

def main():
    # Create tabs for different heatmap types
    tab1, tab2, tab3, tab4 = st.tabs([
        "Population Density", 
        "Health Facilities", 
        "Education", 
        " Economic Activity"
    ])
    
    with tab1:
        st.subheader("Population Distribution and Density")
        st.markdown("Visualize population hotspots across Namibian settlements based on 2011 census data and projections.")
        
        col1, col2 = st.columns([3, 1])
        
        with col2:
            # Controls for population heatmap
            radius = st.slider("Heatmap radius (pixels)", 10, 50, 20, key="pop_radius")
            blur = st.slider("Blur amount", 5, 30, 15, key="pop_blur")
            weight_col = st.selectbox(
                "Weight by",
                ["population_2011", "population_density_km2", "households"],
                format_func=lambda x: x.replace('_', ' ').title()
            )
            
            st.info("ℹ Larger circles indicate higher population concentrations.")
        
        with col1:
            # Create population heatmap
            m = leafmap.Map(center=[-22.0, 17.0], zoom=5, height=600)
            
            df_settlements = create_namibia_settlements_data()
            
            # Add heatmap
            m.add_heatmap(
                df_settlements,
                latitude="latitude",
                longitude="longitude",
                value=weight_col,
                name="Population Heatmap",
                radius=radius,
                blur=blur,
                max_zoom=1
            )
            
            # Add settlement markers with popup info
            for idx, row in df_settlements.iterrows():
                popup = f"""
                <b>{row['settlement']}</b><br>
                Region: {row['region']}<br>
                Population (2011): {row['population_2011']:,.0f}<br>
                Households: {row['households']:,.0f}<br>
                Density: {row['population_density_km2']:.1f}/km²
                """
                m.add_marker(location=[row['latitude'], row['longitude']], popup=popup)
            
            m.to_streamlit()
        
        # Show data table
        with st.expander("View settlement data"):
            st.dataframe(df_settlements.style.format({
                'population_2011': '{:,.0f}',
                'households': '{:,.0f}',
                'population_density_km2': '{:.1f}',
                'avg_household_income_nad': '{:,.0f}'
            }))
    
    with tab2:
        st.subheader("Health Facilities Distribution")
        st.markdown("Explore the distribution of hospitals, clinics, and health facilities across Namibia.")
        
        col1, col2 = st.columns([3, 1])
        
        with col2:
            radius = st.slider("Heatmap radius", 10, 50, 15, key="health_radius")
            facility_type = st.multiselect(
                "Facility types",
                ["District Hospital", "Intermediate Hospital", "Tertiary Hospital", "Clinic", "Private Hospital"],
                default=["District Hospital", "Intermediate Hospital", "Tertiary Hospital"]
            )
            weight_by = st.radio("Weight by", ["beds", "catchment_population"], index=0)
        
        with col1:
            m = leafmap.Map(center=[-22.0, 17.0], zoom=5, height=600)
            
            df_health = create_health_facilities_data()
            
            # Filter by facility type
            df_filtered = df_health[df_health['type'].isin(facility_type)]
            
            if not df_filtered.empty:
                m.add_heatmap(
                    df_filtered,
                    latitude="latitude",
                    longitude="longitude",
                    value=weight_by,
                    name="Health Facilities",
                    radius=radius
                )
                
                # Add markers for major hospitals
                for idx, row in df_filtered.iterrows():
                    popup = f"""
                    <b>{row['facility']}</b><br>
                    Type: {row['type']}<br>
                    Beds: {row['beds']}<br>
                    Catchment: {row['catchment_population']:,.0f}
                    """
                    m.add_marker(location=[row['latitude'], row['longitude']], popup=popup)
            
            m.to_streamlit()
    
    with tab3:
        st.subheader("Education Infrastructure")
        st.markdown("Visualize the distribution of schools and education facilities.")
        
        col1, col2 = st.columns([3, 1])
        
        with col2:
            radius = st.slider("Heatmap radius", 10, 50, 20, key="school_radius")
            school_type = st.multiselect(
                "School types",
                ["Primary", "Secondary", "Combined"],
                default=["Primary", "Secondary", "Combined"]
            )
            weight_col = st.selectbox(
                "Weight by",
                ["enrollment", "teachers"],
                format_func=lambda x: x.title()
            )
        
        with col1:
            m = leafmap.Map(center=[-22.0, 17.0], zoom=5, height=600)
            
            df_schools = create_schools_data()
            df_filtered = df_schools[df_schools['type'].isin(school_type)]
            
            if not df_filtered.empty:
                m.add_heatmap(
                    df_filtered,
                    latitude="latitude",
                    longitude="longitude",
                    value=weight_col,
                    name="Schools",
                    radius=radius
                )
            
            m.to_streamlit()
    
    with tab4:
        st.subheader("Economic Activity Hotspots")
        st.markdown("Explore mining operations, commercial farms, and economic centers.")
        
        col1, col2 = st.columns([3, 1])
        
        with col2:
            radius = st.slider("Heatmap radius", 10, 50, 15, key="econ_radius")
            show_mines = st.checkbox("Show mines", True)
            show_farms = st.checkbox("Show farms", False)
        
        with col1:
            m = leafmap.Map(center=[-22.0, 17.0], zoom=5, height=600)
            
            df_mines, df_farms = create_economic_activity_data()
            
            if show_mines:
                m.add_heatmap(
                    df_mines,
                    latitude="latitude",
                    longitude="longitude",
                    value="employment",
                    name="Mines",
                    radius=radius
                )
                
                # Add mine markers
                for idx, row in df_mines.iterrows():
                    popup = f"""
                    <b>{row['mine']}</b><br>
                    Commodity: {row['commodity']}<br>
                    Employment: {row['employment']}
                    """
                    m.add_marker(location=[row['latitude'], row['longitude']], popup=popup)
            
            if show_farms:
                m.add_heatmap(
                    df_farms,
                    latitude="latitude",
                    longitude="longitude",
                    value="size_ha",
                    name="Farms",
                    radius=radius
                )
            
            m.to_streamlit()
    
    # Data sources and methodology
    st.markdown("---")
    with st.expander("Data Sources & Methodology"):
        st.markdown("""
        **Data Sources:**
        - **NSDI Digital Namibia** - Geospatial data and administrative boundaries
        - **Namibia Statistics Agency (NSA)** - Census 2011 and projections
        - **Ministry of Health and Social Services** - Health facilities registry
        - **Ministry of Education, Arts and Culture** - School locations and enrollment
        - **Chamber of Mines Namibia** - Mining operations data
        
        **Methodology:**
        - Heatmaps are generated using kernel density estimation
        - Point data is weighted by relevant attributes (population, beds, enrollment, etc.)
        - Data is simulated based on actual distributions from NSA reports
        - For official statistics, please contact the respective ministries
        
        **Note:** This is a demonstration using simulated data. For actual policy decisions, 
        please use official data from the Namibia Statistics Agency and relevant ministries.
        """)

if __name__ == "__main__":
    main()