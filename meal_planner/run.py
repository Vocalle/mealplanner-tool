import streamlit as st
import json
import os

# Hintergrundbild-URL aus der Add-on-Konfiguration lesen
options_path = "/data/options.json"
if os.path.exists(options_path):
    with open(options_path) as f:
        options = json.load(f)
    background_url = options.get("background_url", "https://images.unsplash.com/photo-1506744038136-46273834b3fb")
else:
    background_url = "https://images.unsplash.com/photo-1506744038136-46273834b3fb"

# style.css laden und Platzhalter ersetzen
css_path = os.path.join(os.path.dirname(__file__), "style.css")
with open(css_path) as f:
    css = f.read().replace("__BACKGROUND_URL__", background_url)

st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

st.info("Das Hintergrundbild kann in der Add-on-Konfiguration von Home Assistant geändert werden (Option: background_url).")

st.title("Wochenplan")
st.markdown('<div class="block">Hier steht dein Wochenplan-Content...</div>', unsafe_allow_html=True)
