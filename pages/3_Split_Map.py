import streamlit as st
import leafmap.foliumap as leafmap

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

st.title("Split-panel Map")

with st.expander("See data source"):
    st.code(
        """
import leafmap.foliumap as leafmap

# Create a split-panel map with ESA WorldCover layers
m = leafmap.Map()
m.split_map(
    left_layer="ESA WorldCover 2020 S2 FCC", 
    right_layer="ESA WorldCover 2020"
)
m.add_legend(title="ESA Land Cover", builtin_legend="ESA_WorldCover")
m.to_streamlit(height=700)
        """,
        language="python"
    )

# Create the map
try:
    m = leafmap.Map()
    m.split_map(
        left_layer="ESA WorldCover 2020 S2 FCC", 
        right_layer="ESA WorldCover 2020"
    )
    m.add_legend(title="ESA Land Cover", builtin_legend="ESA_WorldCover")
    m.to_streamlit(height=700)
    
except Exception as e:
    st.error(f"An error occurred while loading the split map: {str(e)}")
    st.info("Falling back to a simple map view...")
    
    # Fallback to a simple map
    m = leafmap.Map()
    m.add_basemap("SATELLITE")
    m.to_streamlit(height=700)