import json
import os
import leafmap.foliumap as leafmap
import leafmap.colormaps as cm
import streamlit as st
import requests
from bs4 import BeautifulSoup
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


@st.cache_data
def load_cog_list():
    """Load list of sample COG files"""
    cog_files = [
        "https://opendata.digitalglobe.com/events/california-fire-2020/california-fire-2020_odm_50cm_8bit_cog/california-fire-2020_odm_50cm_8bit_cog_151200-4815600.tif",
        "https://opendata.digitalglobe.com/events/california-fire-2020/california-fire-2020_odm_50cm_8bit_cog/california-fire-2020_odm_50cm_8bit_cog_151200-4816800.tif",
        "https://opendata.digitalglobe.com/events/california-fire-2020/california-fire-2020_odm_50cm_8bit_cog/california-fire-2020_odm_50cm_8bit_cog_151200-4818000.tif",
        "https://opendata.digitalglobe.com/events/mauna-loa-eruption-2022/mauna-loa-2022-11-30/mauna-loa-2022-11-30_10m_cog/mauna-loa-2022-11-30_10m_cog_512000-2144000.tif",
        "https://opendata.digitalglobe.com/events/mauna-loa-eruption-2022/mauna-loa-2022-12-09/mauna-loa-2022-12-09_10m_cog/mauna-loa-2022-12-09_10m_cog_512000-2144000.tif",
    ]
    return cog_files


@st.cache_data
def get_namibia_cog_sources():
    """Get Namibia-specific COG sources from NSDI and other providers"""
    
    namibia_cogs = {
        "Namibia SRTM 30m DEM": {
            "url": "https://s3.amazonaws.com/elevation-tiles-prod/geotiff/15_18018_26172.tif",  # Example - replace with actual NSDI URL
            "description": "Shuttle Radar Topography Mission Digital Elevation Model for Namibia",
            "source": "NASA/USGS",
            "bands": 1,
            "type": "Elevation"
        },
        "Namibia Landsat 8 Mosaic": {
            "url": "https://landsat-pds.s3.amazonaws.com/c1/L8/139/073/LC08_L1TP_139073_20210101_20210307_01_T1/LC08_L1TP_139073_20210101_20210307_01_T1_BQA.TIF",  # Example for Windhoek area
            "description": "Landsat 8 mosaic covering central Namibia",
            "source": "USGS",
            "bands": 11,
            "type": "Satellite Imagery"
        },
        "Namibia Sentinel-2 Mosaic": {
            "url": "https://sentinel-cogs.s3.us-west-2.amazonaws.com/sentinel-s2-l2a-cogs/34/K/DV/2023/1/S2B_34KDV_20230101_0_L2A/B02.tif",  # Example
            "description": "Sentinel-2 10m resolution mosaic",
            "source": "ESA",
            "bands": 12,
            "type": "Satellite Imagery"
        },
        "Namibia Population Density": {
            "url": "https://sedac.ciesin.columbia.edu/downloads/data/gpw-v4/gpw-v4-population-density-rev11/population-density_2020.tif",  # Example - global dataset
            "description": "Gridded population density for Namibia",
            "source": "SEDAC",
            "bands": 1,
            "type": "Demographic"
        },
        "Namibia Land Cover": {
            "url": "https://storage.googleapis.com/earthenginepartners-hansen/GFC-2022-v1.10/Hansen_GFC-2022-v1.10_treecover2000_20S_020E.tif",  # Covers part of Namibia
            "description": "Global Forest Change tree canopy cover",
            "source": "UMD/Google",
            "bands": 1,
            "type": "Land Cover"
        },
        "Namibia Rainfall Annual": {
            "url": "https://data.chc.ucsb.edu/products/CHIRPS-2.0/africa_dekad/tifs/chirps-v2.0.2022.12.3.tif",  # Example CHIRPS data
            "description": "CHIRPS rainfall estimates for Southern Africa",
            "source": "UCSB/CHG",
            "bands": 1,
            "type": "Climate"
        },
        "Namibia Nighttime Lights": {
            "url": "https://eogdata.mines.edu/nighttime_light/annual/v20/2022/2022_vcmcfg/SVDNB_npp_20220101-20221231_global_vcmslcfg_c20230306.tif",  # Global VIIRS data
            "description": "VIIRS Nighttime Lights - Urban areas and settlements",
            "source": "Earth Observation Group",
            "bands": 1,
            "type": "Urban"
        },
        "Namibia Soil Organic Carbon": {
            "url": "https://files.isric.org/soilgrids/latest/data/ocs/ocs_0-30cm_mean.vrt",  # VRT for SoilGrids
            "description": "SoilGrids Organic Carbon content",
            "source": "ISRIC",
            "bands": 1,
            "type": "Soil"
        }
    }
    
    return namibia_cogs


@st.cache_data
def get_palettes():
    """Get list of available colormaps"""
    return list(cm.palettes.keys())


def is_trusted_url(url):
    """Check if URL is from a trusted source"""
    trusted_domains = [
        "opendata.digitalglobe.com",
        "s3.amazonaws.com",
        "landsat-pds.s3.amazonaws.com",
        "sentinel-cogs.s3.us-west-2.amazonaws.com",
        "storage.googleapis.com",
        "data.chc.ucsb.edu",
        "eogdata.mines.edu",
        "files.isric.org",
        "sedac.ciesin.columbia.edu",
        "digitalnamibia.nsa.org.na"  # Add NSDI domain
    ]
    
    for domain in trusted_domains:
        if domain in url:
            return True
    return False


def get_cog_info(url):
    """Get basic information about a COG file"""
    try:
        info = leafmap.cog_info(url)
        return info
    except:
        return None


def app():
    st.title(" Namibia Raster Data Visualization")
    st.markdown(
        """
    An interactive web app for visualizing raster datasets and Cloud Optimized GeoTIFF ([COG](https://www.cogeo.org)) 
    for Namibia. Access data from **NSDI Digital Namibia**, **USGS**, **ESA**, and other global providers.
    The app was built using [streamlit](https://streamlit.io), [leafmap](https://leafmap.org), and [Titiler](https://developmentseed.org/titiler/).
    """
    )

    with st.expander("About Cloud Optimized GeoTIFFs"):
        st.markdown("""
        **Cloud Optimized GeoTIFF (COG)** is a regular GeoTIFF file with an internal structure that allows 
        efficient access to the file from a web server. This enables:
        
        - **Fast visualization** - Only the required tiles are downloaded
        - **Multi-resolution** - Zoom in/out without downloading the full dataset
        - **Band selection** - Choose specific bands to display
        - **Custom colormaps** - Apply different color schemes to single-band data
        
        The data sources below provide COGs that can be visualized directly in your browser.
        """)

    # Load data sources
    cog_list = load_cog_list()
    namibia_cogs = get_namibia_cog_sources()
    
    # Create combined options
    cog_options = ["Select a COG..."] + cog_list + list(namibia_cogs.keys())

    row1_col1, row1_col2 = st.columns([2, 1])

    with row1_col1:
        # Add tabs for different data sources
        source_tab1, source_tab2, source_tab3 = st.tabs(["Sample COGs", "🇳🇦 Namibia Datasets", " Custom URL"])
        
        with source_tab1:
            cog = st.selectbox(
                "Select a sample Cloud Optimized GeoTIFF (COG)",
                cog_list,
                key="sample_cog"
            )
            url = cog
        
        with source_tab2:
            selected_namibia_cog = st.selectbox(
                "Select Namibia-specific raster dataset",
                list(namibia_cogs.keys()),
                key="namibia_cog"
            )
            
            if selected_namibia_cog:
                cog_info = namibia_cogs[selected_namibia_cog]
                st.info(f"**{cog_info['description']}**")
                st.markdown(f"*Source: {cog_info['source']}*")
                st.markdown(f"*Type: {cog_info['type']}*")
                url = cog_info['url']
        
        with source_tab3:
            url = st.text_input(
                "Enter a HTTP URL to a Cloud Optimized GeoTIFF (COG)",
                placeholder="https://...",
                key="custom_url"
            )

    with row1_col2:
        empty = st.empty()

        if url and url != "Select a COG...":
            if is_trusted_url(url):
                try:
                    # Get COG info
                    info = get_cog_info(url)
                    if info:
                        st.success(" Valid COG file")
                        
                        # Display metadata
                        with st.expander("📊 COG Metadata"):
                            if isinstance(info, dict):
                                for key, value in info.items():
                                    if key not in ['bounds', 'band_descriptions']:
                                        st.markdown(f"**{key}:** {value}")
                                    elif key == 'bounds':
                                        st.markdown(f"**bounds:** {value}")
                        
                        # Get bands
                        options = leafmap.cog_bands(url)
                        
                        if len(options) > 3:
                            default = options[:3]
                        else:
                            default = options
                        
                        bands = st.multiselect(
                            "Select bands to display",
                            options,
                            default=default
                        )

                        if len(bands) == 1 or len(bands) == 3:
                            pass
                        else:
                            st.error("Please select one or three bands")
                        
                        # Colormap for single band
                        if len(bands) == 1:
                            palettes = get_palettes()
                            colormap = st.selectbox(
                                "Select a colormap",
                                palettes,
                                index=palettes.index("terrain") if "terrain" in palettes else 0
                            )
                        else:
                            colormap = None
                        
                    else:
                        st.warning("Could not read COG metadata")
                        bands = None
                        colormap = None
                        
                except Exception as e:
                    st.error(f"Error reading COG: {str(e)}")
                    bands = None
                    colormap = None
            else:
                st.error("Please enter a URL from a trusted source")
                bands = None
                colormap = None
        else:
            bands = None
            colormap = None

        # Advanced visualization parameters
        add_params = st.checkbox("Add advanced visualization parameters")
        if add_params:
            vis_params = st.text_area(
                "Enter visualization parameters (JSON)",
                '{"min": 0, "max": 255}',
                help="Example: {'min': 0, 'max': 255, 'nodata': 0}"
            )
            try:
                vis_params = json.loads(vis_params.replace("'", '"'))
            except Exception as e:
                st.error(f"Invalid JSON: {str(e)}")
                vis_params = {}
        else:
            vis_params = {}

        # Submit button
        submit = st.button("Visualize Raster", type="primary", use_container_width=True)

    # Create map
    m = leafmap.Map(center=[-22.0, 17.0], zoom=5, height=700)
    m.add_basemap("OpenStreetMap")

    # Add COG layer if submitted
    if submit and url and url != "Select a COG...":
        if bands:
            try:
                with st.spinner("Loading raster data..."):
                    # Prepare layer name
                    if url in namibia_cogs:
                        layer_name = selected_namibia_cog
                    else:
                        layer_name = os.path.basename(url)[:30]
                    
                    # Add COG layer
                    if colormap and len(bands) == 1:
                        # Single band with colormap
                        m.add_cog_layer(
                            url,
                            bands=bands,
                            name=layer_name,
                            colormap_name=colormap,
                            **vis_params
                        )
                    else:
                        # RGB or custom bands
                        m.add_cog_layer(
                            url,
                            bands=bands,
                            name=layer_name,
                            **vis_params
                        )
                    
                    st.success(f" Successfully added {layer_name}")
                    
                    # Center map on COG bounds
                    try:
                        info = leafmap.cog_info(url)
                        if info and 'bounds' in info:
                            bounds = info['bounds']
                            m.set_center(bounds[0] + bounds[2]/2, bounds[1] + bounds[3]/2, 8)
                    except:
                        pass
                        
            except Exception as e:
                st.error(f"Error adding COG layer: {str(e)}")
        else:
            st.warning("Please select bands first")

    # Add layer control
    m.add_layer_control()
    
    # Display map
    with row1_col1:
        m.to_streamlit(height=700)

    # Examples and help section
    st.markdown("---")
    with st.expander("Namibia Raster Data Resources"):
        st.markdown("""
        ### Available Namibia Raster Datasets
        
        | Dataset | Source | Description | Bands |
        |---------|--------|-------------|-------|
        | **SRTM DEM** | NASA/USGS | 30m elevation data for all Namibia | 1 |
        | **Landsat 8/9** | USGS | 30m multispectral imagery | 11 |
        | **Sentinel-2** | ESA | 10m multispectral imagery | 12 |
        | **MODIS** | NASA | Various products (NDVI, LST, etc.) | Multiple |
        | **CHIRPS Rainfall** | UCSB | Daily/decadal rainfall estimates | 1 |
        | **VIIRS Nightlights** | Earth Observation Group | Nighttime lights for urban mapping | 1 |
        | **SoilGrids** | ISRIC | Soil properties (organic carbon, pH, etc.) | 1 |
        | **Global Forest Change** | UMD/Google | Tree cover, loss, and gain | 1 |
        
        ### Tips for Visualization
        
        - **Single band**: Use with colormaps (e.g., terrain for elevation, viridis for rainfall)
        - **Three bands**: Use as RGB (e.g., 4-3-2 for Landsat false color)
        - **Adjust min/max**: Stretch contrast using visualization parameters
        - **Colormaps**: Choose from sequential, diverging, or categorical schemes
        
        ### Trusted Data Sources
        
        - **NSDI Digital Namibia**: https://digitalnamibia.nsa.org.na
        - **USGS EarthExplorer**: https://earthexplorer.usgs.gov
        - **Copernicus Open Access Hub**: https://scihub.copernicus.eu
        - **NASA Earthdata Search**: https://search.earthdata.nasa.gov
        """)

    # Footer
    st.markdown("---")
    st.markdown(
        """
        ** Note:** This app visualizes Cloud Optimized GeoTIFFs directly from web sources. 
        For large-scale analysis, consider downloading datasets locally. 
        Contact [VTA Namibia](https://www.vtanamibia.com) for custom raster processing services.
        """
    )


if __name__ == "__main__":
    app()