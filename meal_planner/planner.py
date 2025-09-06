import streamlit as st
import json
import os
from translations import DE, EN

# Sprache setzen
if "lang" not in st.session_state:
    st.session_state.lang = "DE"
T = DE if st.session_state.lang == "DE" else EN

# Sidebar Navigation
with st.sidebar:
    st.header(T["nav_header"])
    st.subheader(T["nav_sub"])
    page = st.radio("Seite", [T["nav_plan"], T["nav_manage"]], key="page")

    st.markdown("---")
    st.write("🌐 Sprache")
    if st.button(T["language_toggle"], key="lang_button_sidebar"):
        st.session_state.lang = "EN" if st.session_state.lang == "DE" else "DE"
        st.experimental_rerun()

# Datenpfad
DATA_PATH = "/data/meals.json"

# Lade Daten
if os.path.exists(DATA_PATH):
    with open(DATA_PATH, "r") as f:
        meals = json.load(f)
else:
    meals = {}

# Hauptseite: Wochenplan
if page == T["nav_plan"]:
    st.title(T["title"])
    st.subheader(T["subtitle"])

    weekdays = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
    meals_of_day = ["Frühstück", "Mittagessen", "Abendessen"]

    for day in weekdays:
        st.markdown(f"### {day}")
        cols = st.columns(3)
        for i, meal_time in enumerate(meals_of_day):
            with cols[i]:
                st.markdown(f"**{meal_time}**")
                st.button("Details", key=f"{day}_{meal_time}")

    st.markdown("---")
    st.button(T["edit_plan"])
    st.caption(T["tips"])

# Seite: Mahlzeiten verwalten
elif page == T["nav_manage"]:
    st.title(T["nav_manage"])
    weekday = st.selectbox(T["weekday"], ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"])
    recipe_name = st.text_input(T["recipe_name"])
    ingredients = st.text_area(T["ingredients"])
    instructions = st.text_area(T["instructions"])

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
        st.success(T["save"])

    if weekday in meals:
        st.subheader(f"{weekday}:")
        for meal in meals[weekday]:
            st.markdown(f"**{meal['name']}**")
            st.markdown(f"*{T['ingredients']}:* {meal['ingredients']}")
            st.markdown(f"*{T['instructions']}:* {meal['instructions']}")
            st.markdown("---")
