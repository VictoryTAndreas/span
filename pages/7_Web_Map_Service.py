import ast
import json
import streamlit as st
# Import leafmap.foliumap for the map object methods (Map, add_wms_layer, etc.), and keep the alias `leafmap` for compatibility
import leafmap.foliumap as leafmap 
# Import the top-level leafmap package separately to access utility functions like list_wms_layers
import leafmap as lm_utils 

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
    VTA Namibia at [vtanamibia.com](https://www.vtanamibia.com) | [GitHub](https://github.com/VictoryTAndreas) | [Twitter](https://twitter.com/vicanddotvta) | [YouTube](https://youtube.com/@vtastudios) | [LinkedIn](https://www.linkedin.com/https://www.linkedin.com/company/vta-labs-studios/?originalSubdomain=na)
    """
)

# Define a whitelist of trusted URLs
trusted_urls = [
    "https://services.terrascope.be/wms/v2",
    # Add more trusted URLs here
]


@st.cache_data
def get_layers(url):
    """
    Retrieves the list of available WMS layers from the given URL.
    This function now correctly calls list_wms_layers from the top-level leafmap utility module.
    """
    try:
        options = lm_utils.list_wms_layers(url)
        return options
    except Exception as e:
        # Handle cases where the WMS server is unreachable or the URL is invalid
        print(f"Error fetching WMS layers: {e}")
        return []


def is_trusted_url(url):
    return url in trusted_urls


def app():
    st.title("Web Map Service (WMS)")
    st.markdown(
        """
    This app is a demonstration of loading Web Map Service (WMS) layers. Simply enter the URL of the WMS service
    in the text box below and press Enter to retrieve the layers. Go to https://apps.nationalmap.gov/services to find
    some WMS URLs if needed.
    """
    )

    row1_col1, row1_col2 = st.columns([3, 1.3])
    height = 600
    layers = None
    options = [] # Initialize options

    with row1_col2:

        esa_landcover = "https://services.terrascope.be/wms/v2"
        url = st.text_input(
            "Enter a WMS URL:", value="https://services.terrascope.be/wms/v2"
        )
        empty = st.empty()

        if url:

            if is_trusted_url(url):
                # Call the fixed function
                options = get_layers(url)
            else:
                st.error(
                    "The entered URL is not trusted. Please enter a valid WMS URL."
                )

            default = None
            if url == esa_landcover and options:
                # Set default only if layers were successfully retrieved
                if "WORLDCOVER_2020_MAP" in options:
                    default = ["WORLDCOVER_2020_MAP"]
                else:
                    default = [options[0]] # Fallback to the first layer if available
            
            # Use the retrieved options list
            layers = empty.multiselect(
                "Select WMS layers to add to the map:", options, default=default
            )
            add_legend = st.checkbox("Add a legend to the map", value=True)
            
            legend_text = ""
            if default and default[0] == "WORLDCOVER_2020_MAP":
                # Ensure the key exists before attempting access
                if "ESA_WorldCover" in leafmap.builtin_legends:
                    legend = str(leafmap.builtin_legends["ESA_WorldCover"])
                else:
                    legend = ""
            else:
                legend = ""

            if add_legend:
                legend_text = st.text_area(
                    "Enter a legend as a dictionary {label: color}",
                    value=legend,
                    height=200,
                )

    with row1_col1:
        # Initialize map
        m = leafmap.Map(center=(36.3, 0), zoom=2)

        if layers is not None:
            for layer in layers:
                m.add_wms_layer(
                    url, layers=layer, name=layer, attribution=" ", transparent=True
                )
        if add_legend and legend_text:
            try:
                # Use ast.literal_eval for safer parsing of string representation of dict
                legend_dict = ast.literal_eval(legend_text)
                if isinstance(legend_dict, dict):
                    m.add_legend(legend_dict=legend_dict)
                else:
                    st.warning("Legend format is invalid. Please ensure it is a valid Python dictionary structure.")
            except (ValueError, SyntaxError):
                st.warning("Could not parse legend text. Please ensure it is a valid Python dictionary string (e.g., {'Label': '#ff0000'}).")

        m.to_streamlit(height=height)


app()
