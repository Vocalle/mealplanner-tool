import streamlit as st
import random
import json
import os

# ------------------------------
# Pfad für persistente Daten
# ------------------------------
CONFIG_DIR = os.environ.get("CONFIG", "/data")  # HA Add-on setzt CONFIG automatisch
DATA_FILE = os.path.join(CONFIG_DIR, "meals.json")

# ---------------------------------------------------
# Laden & Speichern
# ---------------------------------------------------
def load_meals():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_meals(meals):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(meals, f, ensure_ascii=False, indent=4)

# ---------------------------------------------------
# Session State initialisieren
# ---------------------------------------------------
if "meals" not in st.session_state:
    st.session_state.meals = load_meals()
if "plan" not in st.session_state:
    st.session_state.plan = {}

days = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]

st.title("🍽️ Wochen-Mahlzeiten-Planer")

# ---------------------------------------------------
# Neue Mahlzeit hinzufügen
# ---------------------------------------------------
meal_name = st.text_input("Neue Mahlzeit hinzufügen")
if st.button("➕ Hinzufügen") and meal_name:
    if meal_name not in st.session_state.meals:
        st.session_state.meals[meal_name] = {"rezept": ""}
        save_meals(st.session_state.meals)
        st.success(f"{meal_name} hinzugefügt!")
    else:
        st.warning("Diese Mahlzeit gibt es schon!")

# ---------------------------------------------------
# Liste der Mahlzeiten mit Detailfeldern
# ---------------------------------------------------
st.subheader("📖 Deine Mahlzeiten")
for meal, details in st.session_state.meals.items():
    with st.expander(meal):
        rezept = st.text_area(f"Rezept/Zutaten für {meal}", details.get("rezept", ""), key=f"rezept_{meal}")
        if rezept != details.get("rezept", ""):
            st.session_state.meals[meal]["rezept"] = rezept
            save_meals(st.session_state.meals)

# ---------------------------------------------------
# Wochenplan generieren
# ---------------------------------------------------
if st.button("🎲 Wochenplan generieren"):
    if st.session_state.meals:
        chosen = random.sample(list(st.session_state.meals.keys()), k=min(len(days), len(st.session_state.meals)))
        while len(chosen) < len(days):
            chosen.append(random.choice(list(st.session_state.meals.keys())))
        st.session_state.plan = {day: meal for day, meal in zip(days, chosen)}
    else:
        st.warning("Bitte zuerst Mahlzeiten hinzufügen!")

# ---------------------------------------------------
# Wochenplan anzeigen
# ---------------------------------------------------
if st.session_state.plan:
    st.subheader("📅 Dein Wochenplan")
    for day, meal in st.session_state.plan.items():
        col1, col2 = st.columns([3,1])
        with col1:
            st.write(f"**{day}**: {meal}")
        with col2:
            if st.button("🔄 Neu würfeln", key=f"reroll_{day}"):
                st.session_state.plan[day] = random.choice(list(st.session_state.meals.keys()))