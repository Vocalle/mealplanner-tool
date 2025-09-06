import streamlit as st
import json
import os
from translations import DE, EN

# Sprachlogik
if "lang" not in st.session_state:
    st.session_state.lang = "DE"
T = DE if st.session_state.lang == "DE" else EN

# Sprachwechsel-Button unten rechts
st.markdown("""
    <style>
    .lang-button {
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 9999;
    }
    </style>
""", unsafe_allow_html=True)

if st.button(T["language_toggle"], key="lang_button"):
    st.session_state.lang = "EN" if st.session_state.lang == "DE" else "DE"
    st.experimental_rerun()

# Titel
st.title(T["title"])

# Datenpfad
DATA_PATH = "/data/meals.json"

# Lade bestehende Daten
if os.path.exists(DATA_PATH):
    with open(DATA_PATH, "r") as f:
        meals = json.load(f)
else:
    meals = {}

# Wochentag auswählen
weekday = st.selectbox(T["weekday"], ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"])

# Rezept eingeben
st.subheader(T["add_recipe"])
recipe_name = st.text_input(T["recipe_name"])
ingredients = st.text_area(T["ingredients"])
instructions = st.text_area(T["instructions"])

# Eintragen
if st.button(T["submit"]):
    if weekday not in meals:
        meals[weekday] = []
    meals[weekday].append({
        "name": recipe_name,
        "ingredients": ingredients,
        "instructions": instructions
    })
    with open(DATA_PATH, "w") as f:
        json.dump(meals, f, indent=2)
    st.success(f"{T['save']}!")

# Bestehende Rezepte anzeigen
if weekday in meals:
    st.subheader(f"{weekday}:")
    for i, meal in enumerate(meals[weekday]):
        st.markdown(f"**{meal['name']}**")
        st.markdown(f"*{T['ingredients']}:* {meal['ingredients']}")
        st.markdown(f"*{T['instructions']}:* {meal['instructions']}")
        st.markdown("---")
