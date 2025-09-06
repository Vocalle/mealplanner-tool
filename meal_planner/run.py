import streamlit as st
import sqlite3
import os
import random

# Sprache initialisieren
if "lang" not in st.session_state:
    st.session_state.lang = "DE"

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

DAYS = {
    "DE": ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"],
    "EN": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
}
CATEGORIES = {
    "DE": ["Vegan", "Vegetarisch", "Fleisch"],
    "EN": ["Vegan", "Vegetarian", "Meat"]
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
    st.session_state.plan = {tag: (meals and random.choice(meals)["id"]) or None for tag in DAYS[st.session_state.lang]}
if "detail" not in st.session_state:
    st.session_state.detail = None
if "lang" not in st.session_state:
    st.session_state.lang = "DE"

# CSS
st.markdown("""
    <style>
    .meal-card {background: #23272b; color: #fff; border-radius: 10px; padding: 16px; margin-bottom: 10px; box-shadow: 0 2px 8px #1115;}
    .category-header {color:#88CCFF;}
    .stButton button { margin: 2px 0;}
    </style>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.title("Navigation")
seiten = {
    "DE": {"Wochenplan": "plan", "Mahlzeiten verwalten": "manage"},
    "EN": {"Weekly Plan": "plan", "Manage Meals": "manage"}
}
choice = st.sidebar.radio("Seite wählen" if st.session_state.lang == "DE" else "Choose page", list(seiten[st.session_state.lang].keys()))
st.session_state.view = seiten[st.session_state.lang][choice]

if st.sidebar.button("Sprache wechseln zu Englisch" if st.session_state.lang == "DE" else "Switch language to German"):
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
    st.title("🗓️ Wochen-Mahlzeiten-Planer" if st.session_state.lang == "DE" else "🗓️ Weekly Meal Planner")
    st.markdown("## Dein Wochenplan" if st.session_state.lang == "DE" else "## Your Weekly Plan")
    cols = st.columns(7)
    for i, tag in enumerate(DAYS[st.session_state.lang]):
        with cols[i]:
            st.markdown(f"**{tag}**", unsafe_allow_html=True)
            meal_id = st.session_state.plan.get(tag)
            meal, _ = get_meal(meal_id)
            with st.container():
                if meal:
                    st.markdown(f"<div class='meal-card'>", unsafe_allow_html=True)
                    st.write(meal['name'])
                    st.write(meal['category'])
                    if st.button("🔄", key=f"reroll_{tag}", help="Neu würfeln" if st.session_state.lang == "DE" else "Reroll"):
                        reroll_day(tag)
                    if st.button("Details", key=f"detail_{tag}"):
                        show_meal_detail(meal_id)
                    st.markdown("</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='meal-card'><i>Kein Gericht verfügbar</i></div>" if st.session_state.lang == "DE" else "<div class='meal-card'><i>No meal available</i></div>", unsafe_allow_html=True)

    if st.button("Woche komplett neu würfeln" if st.session_state.lang == "DE" else "Reroll entire week"):
        meals = get_meals()
        if meals:
            st.session_state.plan = {tag: random.choice(meals)["id"] for tag in DAYS[st.session_state.lang]}
        st.rerun()

    st.divider()
    st.markdown("**Tipp:** Neue Gerichte kannst du im Menü 'Mahlzeiten verwalten' anlegen."" if st.session_state.lang == "DE" else "**Tip:** You can add new meals in the 'Manage Meals' menu.")

# Mahlzeiten verwalten
elif st.session_state.view == "manage":
    st.title("🍽️ Mahlzeiten verwalten" if st.session_state.lang == "DE" else "🍽️ Manage Meals")
    st.markdown("Lege neue Gerichte an, bearbeite oder lösche bestehende." if st.session_state.lang == "DE" else "Add new meals, edit or delete existing ones.")

    with st.expander("➕ Neue Mahlzeit hinzufügen" if st.session_state.lang == "DE" else "➕ Add new meal"):
        with st.form("add_meal_form"):
            name = st.text_input("Gericht" if st.session_state.lang == "DE" else "Meal name", key="add_name")
            category = st.selectbox("Kategorie" if st.session_state.lang == "DE" else "Category", CATEGORIES[st.session_state.lang])
            recipe = st.text_area("Rezept" if st.session_state.lang == "DE" else "Recipe")
            ingredients = st.text_input("Zutaten (Kommagetrennt)" if st.session_state.lang == "DE" else "Ingredients (comma-separated)")
            submitted = st.form_submit_button("Anlegen" if st.session_state.lang == "DE" else "Add")
            if submitted and name and category:
                add_meal(name, category, recipe, ingredients.split(","))
                st.success("Mahlzeit gespeichert!" if st.session_state.lang == "DE" else "Meal saved!")
                st.rerun()

    meals = get_meals()
    for cat in CATEGORIES[st.session_state.lang]:
        st.markdown(f"<h3 class='category-header'>{cat}</h3>", unsafe_allow_html=True)
        cat_meals = [m for m in meals if m["category"] == cat]
        cols = st.columns(4)
        for i, meal in enumerate(cat_meals):
            with cols[i % 4]:
                st.markdown(f"<div class='meal-card'>", unsafe_allow_html=True)
                if meal:
                    st.markdown(f"**{meal['name']}**", unsafe_allow_html=True)
                    if st.button("Details", key=f"detail_manage_{meal['id']}"):
                        show_meal_detail(meal['id'])
                    if st.button("🗑️ Löschen" if st.session_state.lang == "DE" else "🗑️ Delete", key=f"del_{meal['id']}"):
                        delete_and_refresh(meal['id'])
                else:
                    st.markdown("<i>Kein Gericht verfügbar</i>" if st.session_state.lang == "DE" else "<i>No meal available</i>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

# Detailansicht
if st.session_state.detail:
    meal, ings = get_meal(st.session_state.detail)
    if meal:
        st.markdown("---")
        st.markdown(f"### {meal['name']} ({meal['category']})")
        st.markdown("#### Zutaten" if st.session_state.lang == "DE" else "#### Ingredients")
        for ing in ings:
            col1, col2 = st.columns([4,1])
            col1.write(ing["name"])
            if col2.button("🗑️", key=f"del_ing_{meal['id']}_{ing['id']}"):
                delete_ingredient(ing["id"])
                st.rerun()
        new_ing = st.text_input("Neue Zutat" if st.session_state.lang == "DE" else "New ingredient", key=f"new_ing_{meal['id']}")
        if st.button("Zutat hinzufügen" if st.session_state.lang == "DE" else "Add ingredient", key=f"add_ing_{meal['id']}"):
            if new_ing.strip():
                add_ingredient(meal['id'], new_ing.strip())
                st.rerun()
        st.markdown("#### Rezept" if st.session_state.lang == "DE" else "#### Recipe")
        recipe = st.text_area("Rezept bearbeiten" if st.session_state.lang == "DE" else "Edit recipe", meal["recipe"] or "", key=f"recipe_{meal['id']}")
        if st.button("Rezept speichern" if st.session_state.lang == "DE" else "Save recipe", key=f"save_recipe_{meal['id']}"):
            update_recipe(meal['id'], recipe)
            st.success("Rezept gespeichert!" if st.session_state.lang == "DE" else "Recipe saved!")
        if st.button("Zurück" if st.session_state.lang == "DE" else "Back", key=f"back_{meal['id']}"):
            st.session_state.detail = None
            st.rerun()
    else:
        st.error("Dieses Gericht existiert nicht mehr." if st.session_state.lang == "DE" else "This meal no longer exists.")
        if st.button("Zurück zum Plan" if st.session_state.lang == "DE" else "Back to plan"):
            st.session_state.detail = None
            st.rerun()
```
