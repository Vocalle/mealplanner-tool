import streamlit as st
import sqlite3
import os
import random

# --- DB-Setup ---
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
    # Beispielgericht
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

# --- Datenbank-Funktionen ---
def get_meals():
    with get_db() as conn:
        return conn.execute("SELECT * FROM meal").fetchall()

def get_meal(meal_id):
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

# --- Session State für Navigation ---
if "view" not in st.session_state:
    st.session_state.view = "plan"
if "plan" not in st.session_state:
    meals = get_meals()
    st.session_state.plan = {tag: (meals and random.choice(meals)["id"]) or None for tag in DAYS}

# --- CSS für dunkles Theme & Kacheln ---
st.markdown("""
    <style>
    .meal-card {background: #23272b; color: #fff; border-radius: 10px; padding: 16px; margin-bottom: 10px; box-shadow: 0 2px 8px #1115;}
    .meal-btn {display:inline-block; margin:4px;}
    .stTextInput>div>div>input { background: #222; color: #fff; }
    .stTextArea textarea { background: #222; color: #fff; }
    .category-header {color:#88CCFF;}
    </style>
""", unsafe_allow_html=True)

# --- Navigation ---
st.sidebar.title("Navigation")
seiten = {"Wochenplan": "plan", "Mahlzeiten verwalten": "manage"}
choice = st.sidebar.radio("Seite wählen", list(seiten.keys()))
st.session_state.view = seiten[choice]

# --- Wochenplan ---
if st.session_state.view == "plan":
    st.title("🗓️ Wochen-Mahlzeiten-Planer")

    st.markdown("### Dein Wochenplan")
    cols = st.columns(7)
    for i, tag in enumerate(DAYS):
        with cols[i]:
            meal_id = st.session_state.plan.get(tag)
            if meal_id:
                meal, _ = get_meal(meal_id)
                st.markdown(f"<div class='meal-card'>", unsafe_allow_html=True)
                st.markdown(f"**{tag}**<br><b>{meal['name']}</b><br><span style='font-size:0.9em;'>{meal['category']}</span>", unsafe_allow_html=True)
                st.button("🔄", key=f"reroll_{tag}", help="Neu würfeln", on_click=lambda d=tag: reroll_day(d))
                st.button("Details", key=f"detail_{tag}", on_click=lambda mid=meal_id: show_meal_detail(mid))
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='meal-card'>{tag}<br><i>Kein Gericht</i></div>", unsafe_allow_html=True)

    if st.button("Woche komplett neu würfeln"):
        meals = get_meals()
        if meals:
            st.session_state.plan = {tag: random.choice(meals)["id"] for tag in DAYS}
        st.experimental_rerun()

    st.divider()
    st.markdown("**Tipp:** Neue Gerichte kannst du im Menü 'Mahlzeiten verwalten' anlegen.")

# --- Mahlzeiten verwalten ---
elif st.session_state.view == "manage":
    st.title("🍽️ Mahlzeiten verwalten")
    st.markdown("Lege neue Gerichte an, bearbeite oder lösche bestehende.")

    with st.expander("➕ Neue Mahlzeit hinzufügen"):
        with st.form("add_meal_form"):
            name = st.text_input("Gericht", key="add_name")
            category = st.selectbox("Kategorie", CATEGORIES)
            recipe = st.text_area("Rezept")
            ingredients = st.text_input("Zutaten (Kommagetrennt)")
            submitted = st.form_submit_button("Anlegen")
            if submitted and name and category:
                add_meal(name, category, recipe, ingredients.split(","))
                st.success("Mahlzeit gespeichert!")
                st.experimental_rerun()

    # Mahlzeiten gruppiert nach Kategorie
    meals = get_meals()
    for cat in CATEGORIES:
        st.markdown(f"<h3 class='category-header'>{cat}</h3>", unsafe_allow_html=True)
        cat_meals = [m for m in meals if m["category"] == cat]
        cols = st.columns(4)
        for i, meal in enumerate(cat_meals):
            with cols[i % 4]:
                st.markdown(f"<div class='meal-card'>", unsafe_allow_html=True)
                st.markdown(f"**{meal['name']}**", unsafe_allow_html=True)
                st.button("Details", key=f"detail_manage_{meal['id']}", on_click=lambda mid=meal['id']: show_meal_detail(mid))
                st.button("🗑️ Löschen", key=f"del_{meal['id']}", on_click=lambda mid=meal['id']: delete_and_refresh(mid))
                st.markdown("</div>", unsafe_allow_html=True)

# --- Detailansicht (Modal) ---
def show_meal_detail(meal_id):
    meal, ings = get_meal(meal_id)
    st.session_state.detail = meal_id
    st.markdown("---")
    st.markdown(f"### {meal['name']} ({meal['category']})")
    st.markdown("#### Zutaten")
    for ing in ings:
        col1, col2 = st.columns([4,1])
        col1.write(ing["name"])
        if col2.button("🗑️", key=f"del_ing_{ing['id']}"):
            delete_ingredient(ing["id"])
            st.experimental_rerun()
    new_ing = st.text_input("Neue Zutat", key="new_ing")
    if st.button("Zutat hinzufügen"):
        if new_ing.strip():
            add_ingredient(meal_id, new_ing.strip())
            st.experimental_rerun()
    st.markdown("#### Rezept")
    recipe = st.text_area("Rezept bearbeiten", meal["recipe"] or "")
    if st.button("Rezept speichern"):
        update_recipe(meal_id, recipe)
        st.success("Rezept gespeichert!")
    if st.button("Zurück"):
        del st.session_state.detail
        st.experimental_rerun()

def reroll_day(day):
    meals = get_meals()
    current = st.session_state.plan.get(day)
    options = [m for m in meals if m["id"] != current]
    if options:
        st.session_state.plan[day] = random.choice(options)["id"]
    st.experimental_rerun()

def delete_and_refresh(meal_id):
    delete_meal(meal_id)
    st.experimental_rerun()

# --- Detailanzeige Modal (automatisch öffnen) ---
if "detail" in st.session_state:
    show_meal_detail(st.session_state.detail)
