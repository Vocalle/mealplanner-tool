import streamlit as st
import json
import os

# Optionen aus der Add-on-Konfig laden
options_path = "/data/options.json"
if os.path.exists(options_path):
    with open(options_path) as f:
        options = json.load(f)
    background_url = options.get("background_url", "https://images.unsplash.com/photo-1506744038136-46273834b3fb")
else:
    background_url = "https://images.unsplash.com/photo-1506744038136-46273834b3fb"

# Dynamisches CSS mit Hintergrundbild
css = f"""
body {{
    background-image: url('{background_url}');
    background-size: cover;
    background-position: center;
}}
/* Dein weiteres CSS ... */
"""
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# ... Rest deiner Streamlit-App ...
