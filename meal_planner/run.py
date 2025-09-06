import streamlit as st
import os

# Speicherort für das Hintergrundbild im Add-on
IMAGE_PATH = "/data/background.jpg"

# 1. Upload-Widget in der Sidebar
st.sidebar.header("Hintergrundbild")
uploaded_file = st.sidebar.file_uploader(
    "Eigenes Hintergrundbild hochladen (JPG/PNG)", type=["jpg", "jpeg", "png"]
)
if uploaded_file is not None:
    with open(IMAGE_PATH, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.sidebar.success("Bild gespeichert! Seite ggf. neuladen.")

# 2. Hintergrundbild wählen (hochgeladen oder Fallback)
if os.path.exists(IMAGE_PATH):
    # Achtung: Streamlit in HA Add-ons kann lokale Images nicht immer direkt anzeigen.
    # Base64-Embeddung als Fallback für volle Kompatibilität:
    import base64
    with open(IMAGE_PATH, "rb") as img_file:
        img_bytes = img_file.read()
        encoded = base64.b64encode(img_bytes).decode()
    background_url = f"data:image/jpeg;base64,{encoded}"
else:
    # Standardbild
    background_url = "https://images.unsplash.com/photo-1506744038136-46273834b3fb"

# 3. Custom CSS einbinden
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

# 4. Beispiel-Content (hier baust du deine UI weiter aus)
st.title("Wochenplan")
st.markdown('<div class="block">Hier steht dein Wochenplan-Content...</div>', unsafe_allow_html=True)
