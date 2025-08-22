"""
Streamlit Cloud Entry Point for Recommendation System Frontend

This file serves as the main entry point for Streamlit Cloud deployment.
Access your beautiful 3D bubble recommendation interface here!
"""
import os
import sys
from pathlib import Path
import streamlit as st

# Add deployment/streamlit to Python path
streamlit_path = Path(__file__).parent / "deployment" / "streamlit"
sys.path.insert(0, str(streamlit_path))

# Configure API URL for Streamlit Cloud
try:
    # Try to get from Streamlit secrets first (Streamlit Cloud)
    API_URL = st.secrets.get("RECO_API_URL", "")
except:
    # Fallback to environment variables (local development)
    API_URL = os.getenv("RECO_API_URL") or os.getenv("FUNCTION_URL") or ""

# Set the API URL for the imported app
os.environ["RECO_API_URL"] = API_URL or "https://ocp9funcapp-recsys.azurewebsites.net/api/reco"

# Import and run the main app
from app import *  # This will execute the main Streamlit app