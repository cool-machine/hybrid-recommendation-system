"""
Streamlit Cloud Entry Point for Hybrid Recommendation System

This file serves as the main entry point for Streamlit Cloud deployment.
It properly imports and runs the recommendation system frontend.
"""
import sys
import os
from pathlib import Path

# Add deployment/streamlit directory to Python path
streamlit_dir = Path(__file__).parent / "deployment" / "streamlit"
if streamlit_dir.exists():
    sys.path.insert(0, str(streamlit_dir))

# Import the main streamlit app
try:
    # First try to import from streamlit_app.py in deployment folder
    from streamlit_app import *
except ImportError:
    try:
        # Fallback to app.py
        from app import *
    except ImportError:
        import streamlit as st
        st.error("Could not find the Streamlit app files. Please check the deployment/streamlit directory.")
        st.stop()