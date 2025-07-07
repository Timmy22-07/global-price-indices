# core/welcome.py
# -----------------------------------------------------
# Welcome tab for Global Price Indices app
# -----------------------------------------------------
import streamlit as st

def display_welcome_tab():
    st.markdown("""
    ### 🏠 Welcome

    This project is a data exploration tool designed to help users better understand the global cost of living, inflation, purchasing power, and exchange rates, through clean interfaces and accessible datasets.

    It focuses on clarity, speed, and simplicity:

    • Only a selection of core datasets is currently loaded to ensure fast performance, but I can add more on demand.  
    • If you would like to explore more data or contribute suggestions, feel free to contact me.

    📬 **Contact**: abadjifinlmi@gmail.com  
    🧠 **Goal**: Make public data easier to use, faster to access, and more meaningful.

    Thank you for visiting. Enjoy your exploration!
    """)
