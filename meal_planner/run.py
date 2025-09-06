import streamlit as st
import os

# Speicherort für das hochgeladene Bild
IMAGE_PATH = "/data/background.jpg"

# 1. Bild-Upload-Widget
st.sidebar.header("Hintergrundbild")
uploaded_file = st.sidebar.file_uploader(
    "Eigenes Hintergrundbild hochladen (JPG/PNG)", type=["jpg", "jpeg", "png"]
)
if uploaded_file is not None:
    with open(IMAGE_PATH, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.sidebar.success("Bild gespeichert! Seite ggf. neuladen.")

# 2. Bild-URL festlegen: Hochgeladenes Bild oder Standardbild
if os.path.exists(IMAGE_PATH):
    # Lokale Datei verwenden (Streamlit unterstützt file-URLs im Ingress-Container)
    background_url = IMAGE_PATH
else:
    # Standardbild
    background_url = "https://images.unsplash.com/photo-1506744038136-46273834b3fb"

# 3. CSS einbinden
css = f"""
body {{
    background-image: url('{background_url}');
    background-size: cover;
    background-position: center;
}}
/* Optional: Style für Cards/Blöcke */
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

# 4. Beispiel-Content (dein eigentlicher Wochenplan etc.)
st.title("Wochenplan")
st.markdown('<div class="block">Hier steht dein Wochenplan-Content...</div>', unsafe_allow_html=True)
