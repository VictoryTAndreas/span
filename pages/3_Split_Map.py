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
    VTA Namibia at [vtanamibia.com](https://www.vtanamibia.com) | [GitHub](https://github.com/VictoryTAndreas) | [Twitter](https://twitter.com/vicanddotvta) | [YouTube](https://youtube.com/@vtastudios) | [LinkedIn](https://www.linkedin.com/https://www.linkedin.com/company/vta-labs-studios/?originalSubdomain=na)
    """
)

st.title("Split-panel Map")

with st.expander("See data source"):
    with st.echo():
        m = leafmap.Map()
        m.split_map(
            left_layer="ESA WorldCover 2020 S2 FCC", right_layer="ESA WorldCover 2020"
        )
        m.add_legend(title="ESA Land Cover", builtin_legend="ESA_WorldCover")

m.to_streamlit(height=700)
