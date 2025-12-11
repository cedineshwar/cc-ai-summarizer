# pages/2_🌍_Mapping_Demo.py
import streamlit as st
import pandas as pd
import numpy as np
from src.utils import add_footer

st.markdown("# Mapping Demo 🌍")
st.write("This page shows a map.")

df = pd.DataFrame(
    np.random.randn(1000, 2) / [50, 50] + [37.76, -122.4],
    columns=['lat', 'lon']
)
st.map(df)

# Add footer to the page
add_footer()
