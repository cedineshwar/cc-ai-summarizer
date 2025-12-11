# pages/1_📈_Plotting_Demo.py
import streamlit as st
import pandas as pd
import numpy as np
from src.utils import add_footer

st.markdown("# Plotting Demo 📈")
st.write("This page demonstrates plotting capabilities.")

chart_data = pd.DataFrame(
    np.random.randn(20, 3),
    columns=['a', 'b', 'c']
)
st.line_chart(chart_data)

# Add footer to the page
add_footer()
