import streamlit as st
import sqlite3
import os
import random

# Sprachunterstützung
DE = {
    "nav_title": "Navigation",
    "nav_page": "Seite wählen",
    "language_toggle": "Sprache wechseln zu Englisch",
    "plan_title": "🗓️ Wochen-Mahlzeiten-Planer",
    "plan_subtitle": "Dein Wochenplan",
    "tip": "Tipp: Neue Gerichte kannst du im Menü 'Mahlzeiten verwalten' anlegen.",
    "reroll_week": "Woche komplett neu würfeln",
    "no_meal": "Kein Gericht verfügbar",
    "manage_title": "🍽️ Mahlzeiten verwalten",
    "manage_subtitle": "Lege neue Gerichte an, bearbeite oder lösche bestehende.",
    "add_meal": "➕ Neue Mahlzeit hinzufügen",
    "dish": "Gericht",
    "category": "Kategorie",
    "recipe": "Rezept",
    "ingredients": "Zutaten (Kommagetrennt)",
    "submit": "Anlegen",
    "saved": "Mahlzeit gespeichert!",
    "details": "Details",
    "delete": "🗑️ Löschen",
    "ingredient": "Neue Zutat",
    "add_ingredient": "Zutat hinzufügen",
    "edit_recipe": "Rezept bearbeiten",
    "save_recipe": "Rezept speichern",
    "back": "Zurück",
    "no_longer_exists": "Dieses Gericht existiert nicht mehr.",
    "back_to_plan": "Zurück zum Plan"
}

EN = {
    "nav_title": "Navigation",
    "nav_page": "Choose page",
    "language_toggle": "Sprache wechseln zu Deutsch",
    "plan_title": "🗓️ Weekly Meal Planner",
    "plan_subtitle": "Your Weekly Plan",
    "tip": "Tip: You can add new meals in the 'Manage Meals' section.",
    "reroll_week": "Reroll entire week",
    "no_meal": "No meal available",
    "manage_title": "🍽️ Manage Meals",
    "manage_subtitle": "Add, edit or delete meals.",
    "add_meal": "➕ Add new meal",
    "dish": "Dish",
    "category": "Category",
    "recipe": "Recipe",
    "ingredients": "Ingredients (comma-separated)",
    "submit": "Submit",
    "saved": "Meal saved!",
    "details": "Details",
    "delete": "🗑️ Delete",
    "ingredient": "New ingredient",
    "add_ingredient": "Add ingredient",
    "edit_recipe": "Edit recipe",
    "save_recipe": "Save recipe",
    "back": "Back",
    "no_longer_exists": "This meal no longer exists.",
    "back_to_plan": "Back to plan"
}

# Sprache setzen
if "lang" not in st.session_state:
    st.session_state.lang = "DE"
T = DE if st.session_state.lang == "DE" else EN

# Datenbankpfad
DB_PATH = "/data/meals.db" if os.path.exists("/data") else "meals.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS meal (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        recipe TEXT
    )""")
    c.execute("""
    CREATE TABLE IF NOT EXISTS ingredient (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        meal_id INTEGER,
        FOREIGN KEY(meal_id) REFERENCES meal(id) ON DELETE CASCADE
    )""")
    conn.commit()
    c.execute("SELECT count(*) FROM meal")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO meal (name, category, recipe) VALUES (?, ?, ?)",
                  ("Spaghetti Bolognese", "Fleisch", "Ein Klassiker..."))
        meal_id = c.lastrowid
        for ing in ["Spaghetti", "Hackfleisch", "Tomatensauce"]:
            c.execute("INSERT INTO ingredient (name, meal_id) VALUES (?, ?)", (ing, meal_id))
        conn.commit()
    conn.close()

init_db()

DAYS = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
CATEGORIES = ["Vegan", "Vegetarisch", "Fleisch"]

def get_meals():
    with get_db() as conn:
        return conn.execute("SELECT * FROM meal").fetchall()

def get_meal(meal_id):
    if meal_id is None:
        return None, []
    with get_db() as conn:
        meal = conn.execute("SELECT * FROM meal WHERE id=?", (meal_id,)).fetchone()
        ings = conn.execute("SELECT * FROM ingredient WHERE meal_id=?", (meal_id,)).fetchall()
    return meal, ings

def add_meal(name, category, recipe, ingredients):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO meal (name, category, recipe) VALUES (?, ?, ?)", (name, category, recipe))
        meal_id = cur.lastrowid
        for ing in ingredients:
            if ing.strip():
                cur.execute("INSERT INTO ingredient (name, meal_id) VALUES (?, ?)", (ing.strip(), meal_id))
        conn.commit()

def delete_meal(meal_id):
    with get_db() as conn:
        conn.execute("DELETE FROM meal WHERE id=?", (meal_id,))
        conn.commit()

def update_recipe(meal_id, recipe):
    with get_db() as conn:
        conn.execute("UPDATE meal SET recipe=? WHERE id=?", (recipe, meal_id))
        conn.commit()

def add_ingredient(meal_id, name):
    with get_db() as conn:
        conn.execute("INSERT INTO ingredient (name, meal_id) VALUES (?, ?)", (name, meal_id))
        conn.commit()

def delete_ingredient(ing_id):
    with get_db() as conn:
        conn.execute("DELETE FROM ingredient WHERE id=?", (ing_id,))
        conn.commit()

# Session State
if "view" not in st.session_state:
    st.session_state.view = "plan"
if "plan" not in st.session_state:
    meals = get_meals()
    st.session_state.plan = {tag: (meals and random.choice(meals)["id"]) or None for tag in DAYS}
if "detail" not in st.session_state:
    st.session_state.detail = None

# Custom CSS
st.markdown("""
    <style>
    body {
        background-image: url('__BACKGROUND_URL__');
        background-size: cover;
        background-position: center;
    }
    .block {
        background: rgba(0,0,0,0.6);
        border-radius: 12px;
        margin: 16px 0;
        padding: 24px;
        color: #fff;
        box-shadow: 0 4px 16px rgba(0,0,0,0.3);
    }
    .meal-card {background: #23272b; color: #fff; border-radius: 10px; padding: 16px; margin-bottom: 10px; box-shadow: 0 2px 8px #1115;}
    .category-header {color:#88CCFF;}
    .stButton button { margin: 2px 0;}
    </style>
""", unsafe_allow_html=True)

# Sidebar Navigation
st.sidebar.title(T["nav_title"])
seiten = {"Wochenplan": "plan", "Mahlzeiten verwalten": "manage"} if st.session_state.lang == "DE" else {"Weekly Plan": "plan", "Manage Meals": "manage"}
choice = st.sidebar.radio(T["nav_page"], list(seiten.keys()))
st.session_state.view = seiten[choice]

st.sidebar.markdown("---")
if st.sidebar.button(T["language_toggle"], key="lang_button_sidebar"):
    st.session_state.lang = "EN" if st.session_state.lang == "DE" else "DE"
    st.rerun()

# Hilfsfunktionen
def reroll_day(day):
    meals = get_meals()
    current = st.session_state.plan.get(day)
    options = [m for m in meals if m["id"] != current]
    if options:
        st.session_state.plan[day] = random.choice(options)["id"]
    st.rerun()

def delete_and_refresh(meal_id):
    delete_meal(meal_id)
    st.rerun()

def show_meal_detail(meal_id):
    st.session_state.detail = meal_id
    st.rerun()

# Wochenplan
if st.session_state.view == "plan":
    st.title(T["plan_title"])
    st.markdown(f"## {T['plan_subtitle']}")
    cols = st.columns(7
