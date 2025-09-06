import streamlit as st
import sqlite3
import os
import random

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
        c.execute(
            "INSERT INTO meal (name, category, recipe) VALUES (?, ?, ?)",
            ("Spaghetti Bolognese", "Fleisch", "Ein Klassiker...")
        )
        meal_id = c.lastrowid
        for ing in ["Spaghetti", "Hackfleisch", "Tomatensauce"]:
            c.execute(
                "INSERT INTO ingredient (name, meal_id) VALUES (?, ?)",
                (ing, meal_id)
            )
        conn.commit()
    conn.close()

init_db()

# interne Keys
CATEGORIES   = ["Vegan", "Vegetarisch", "Fleisch"]
DAYS_DE      = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]

# UI-Labels & Übersetzungen
UI = {
    "lang_radio":    {"DE": "Sprache",          "EN": "Language"},
    "plan_title":    {"DE": "🗓️ Wochen-Mahlzeiten-Planer", "EN": "🗓️ Weekly Meal Planner"},
    "plan_header":   {"DE": "## Dein Wochenplan","EN": "## Your Weekly Plan"},
    "reroll":        {"DE": "🔄 Neu würfeln",   "EN": "🔄 Reroll"},
    "reroll_help":   {"DE": "Neu würfeln",      "EN": "Reroll this day"},
    "details":       {"DE": "ℹ️ Details",       "EN": "ℹ️ Details"},
    "delete":        {"DE": "🗑️ Löschen",       "EN": "🗑️ Delete"},
    "reroll_week":   {"DE": "Woche komplett neu würfeln","EN":"Reroll entire week"},
    "manage_title":  {"DE": "🍽️ Mahlzeiten verwalten", "EN": "🍽️ Manage Meals"},
    "manage_desc":   {"DE": "Lege neue Gerichte an, bearbeite oder lösche bestehende.",
                      "EN": "Add, edit or delete meals."},
    "new_meal":      {"DE": "➕ Neue Mahlzeit hinzufügen","EN":"➕ Add New Meal"},
    "form_name":     {"DE": "Gericht",          "EN": "Meal name"},
    "form_category": {"DE": "Kategorie",        "EN": "Category"},
    "form_recipe":   {"DE": "Rezept",           "EN": "Recipe"},
    "form_ings":     {"DE": "Zutaten (Kommagetrennt)","EN":"Ingredients (comma separated)"},
    "add_button":    {"DE": "✔️ Anlegen",       "EN": "✔️ Create"},
    "success_add":   {"DE": "Mahlzeit gespeichert!","EN":"Meal saved!"},
    "tip":           {"DE": "**Tipp:** Neue Gerichte kannst du im Menü 'Mahlzeiten verwalten' anlegen.",
                      "EN":"**Tip:** You can add new meals under 'Manage Meals'."},
    "back":          {"DE": "⬅️ Zurück",         "EN": "⬅️ Back"},
    "no_exist":      {"DE": "Dieses Gericht existiert nicht mehr.","EN": "This meal no longer exists."},
}

# Farben pro Kategorie
CATEGORY_COLORS = {
    "Vegan":      "#27ae60",
    "Vegetarisch":"#f1c40f",
    "Fleisch":    "#c0392b"
}

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
        cur.execute("INSERT INTO meal (name, category, recipe) VALUES (?, ?, ?)",
                    (name, category, recipe))
        meal_id = cur.lastrowid
        for ing in ingredients:
            if ing.strip():
                cur.execute("INSERT INTO ingredient (name, meal_id) VALUES (?, ?)",
                            (ing.strip(), meal_id))
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
        conn.execute("INSERT INTO ingredient (name, meal_id) VALUES (?, ?)",
                     (name, meal_id))
        conn.commit()

def delete_ingredient(ing_id):
    with get_db() as conn:
        conn.execute("DELETE FROM ingredient WHERE id=?", (ing_id,))
        conn.commit()

# Session State initialisieren
for key, default in [
    ("view", "plan"), ("plan", None),
    ("detail", None), ("lang", "DE")
]:
    if key not in st.session_state:
        st.session_state[key] = default

# Sidebar: Sprache
lang = st.sidebar.radio(
    UI["lang_radio"][st.session_state.lang],
    options=["DE", "EN"],
    index=0 if st.session_state.lang == "DE" else 1,
    key="lang"
)

# Woche initial befüllen
if st.session_state.plan is None:
    meals = get_meals()
    st.session_state.plan = {
        tag: (meals and random.choice(meals)["id"]) or None
        for tag in DAYS_DE
    }

# Dünneres CSS-Upgrade
st.markdown("""
    <style>
    .meal-card {
      color: #fff;
      padding: 0.25rem 0.5rem;
      margin-bottom: 0.25rem;
      border-radius: 6px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.15);
      font-size: 0.85rem;
    }
    .stButton > button {
      padding: 0.2rem 0.4rem;
      margin: 0.1rem;
      font-size: 0.7rem;
      border-radius: 6px;
      background-color: #444;
      color: #fff;
      border: none;
    }
    .stButton > button:hover {
      background-color: #555;
    }
    </style>
""", unsafe_allow_html=True)

# Navigation
st.sidebar.title(UI["manage_title"][lang])
pages = {
    "🗓️ " + UI["plan_title"][lang]: "plan",
    UI["manage_title"][lang]: "manage"
}
choice = st.sidebar.radio("", list(pages.keys()))
st.session_state.view = pages[choice]

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
    st.title(UI["plan_title"][lang])
    st.markdown(UI["plan_header"][lang])
    cols = st.columns(7)
    for i, tag in enumerate(DAYS_DE):
        label = tag  # immer Deutsch in Plan
        meal_id = st.session_state.plan.get(tag)
        meal, _ = get_meal(meal_id)
        with cols[i]:
            st.markdown(f"**{label}**", unsafe_allow_html=True)
            if meal:
                color = CATEGORY_COLORS.get(meal["category"], "#333")
                st.markdown(
                    f"<div class='meal-card' style='background:{color}'>",
                    unsafe_allow_html=True
                )
                st.write(meal["name"])
                if st.button(UI["details"][lang], key=f"detail_{tag}"):
                    show_meal_detail(meal_id)
                if st.button(
                    UI["reroll"][lang],
                    key=f"reroll_{tag}",
                    help=UI["reroll_help"][lang]
                ):
                    reroll_day(tag)
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.markdown(
                    "<div class='meal-card' style='background:#555'><i>–</i></div>",
                    unsafe_allow_html=True
                )

    if st.button(UI["reroll_week"][lang]):
        meals = get_meals()
        st.session_state.plan = {
            tag: (meals and random.choice(meals)["id"]) or None
            for tag in DAYS_DE
        }

I truncated, but enough.
