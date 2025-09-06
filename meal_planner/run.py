import streamlit as st
import json
import os

# 1. Hintergrundbild-URL aus der Add-on-Konfiguration lesen
options_path = "/data/options.json"
if os.path.exists(options_path):
    with open(options_path) as f:
        options = json.load(f)
    background_url = options.get("background_url", "https://images.unsplash.com/photo-1506744038136-46273834b3fb")
else:
    background_url = "https://images.unsplash.com/photo-1506744038136-46273834b3fb"

# 2. CSS für das Hintergrundbild einbinden
css = f"""
body {{
    background-image: url('{background_url}');
    background-size: cover;
    background-position: center;
}}
.block {{
    background: rgba(0,0,0,0.6);
    border-radius: 12px;
    margin: 16px 0;
    padding: 24px;
    color: #fff;
    box-shadow: 0 4px 16px rgba(0,0,0,0.3);
}}
"""
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# 3. Hinweis für den User (optional)
st.info("Das Hintergrundbild kann in der Add-on-Konfiguration von Home Assistant geändert werden (Option: background_url).")

# 4. Dein weiterer Content...
st.title("Wochenplan")
st.markdown('<div class="block">Hier steht dein Wochenplan-Content...</div>', unsafe_allow_html=True)
