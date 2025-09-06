import streamlit as st
import sqlite3
import os
import random

# ----------------------------
# 1. Datenbank-Pfad & Init
# ----------------------------
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
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS ingredient (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            meal_id INTEGER,
            FOREIGN KEY(meal_id) REFERENCES meal(id) ON DELETE CASCADE
        )
    """)
    conn.commit()
    c.execute("SELECT count(*) FROM meal")
    if c.fetchone()[0] == 0:
        # Beispiel-Datensatz
        c.execute(
            "INSERT INTO meal (name, category, recipe) VALUES (?, ?, ?)",
            ("Spaghetti Bolognese", "Meat", "Ein Klassiker…")
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

# ----------------------------
# 2. Sprach-abhängige Werte
# ----------------------------
if "lang" not in st.session_state:
    st.session_state.lang = "DE"  # Start mit Deutsch

DAYS = {
    "DE": ["Montag","Dienstag","Mittwoch","Donnerstag","Freitag","Samstag","Sonntag"],
    "EN": ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
}

# Intern speichern wir immer englische Kategorien
INTERNAL_CATEGORIES = ["Vegan","Vegetarian","Meat"]
DISPLAY_CATEGORIES = {
    "DE": ["Vegan","Vegetarisch","Fleisch"],
    "EN": ["Vegan","Vegetarian","Meat"]
}

CATEGORY_COLORS = {
    "Vegan": "#27ae60",
    "Vegetarian": "#f1c40f",
    "Meat": "#c0392b"
}

# ----------------------------
# 3. DB-Funktionen
# ----------------------------
def get_meals():
    with get_db() as conn:
        return conn.execute("SELECT * FROM meal").fetchall()

def get_meal(meal_id):
    if not meal_id:
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
        mid = cur.lastrowid
        for ing in ingredients:
            if ing.strip():
                cur.execute("INSERT INTO ingredient (name, meal_id) VALUES (?, ?)",
                            (ing.strip(), mid))
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

# ----------------------------
# 4. Session State Defaults
# ----------------------------
if "view" not in st.session_state:
    st.session_state.view = "plan"
if "plan" not in st.session_state:
    st.session_state.plan = None
if "detail" not in st.session_state:
    st.session_state.detail = None

# ----------------------------
# 5. Sidebar: Sprache & Navigation
# ----------------------------
with st.sidebar:
    st.title("Settings")
    # Sprachwahlschalter
    lang = st.radio(
        "Language" if st.session_state.lang=="EN" else "Sprache",
        options=["DE","EN"],
        index=0 if st.session_state.lang=="DE" else 1,
        key="lang"
    )
    # Navigation
    pages = {
        "DE": {"Wochenplan":"plan","Mahlzeiten verwalten":"manage"},
        "EN": {"Weekly Plan":"plan","Manage Meals":"manage"}
    }[lang]
    choice = st.radio("", list(pages.keys()))
    st.session_state.view = pages[choice]

# ----------------------------
# 6. Wochenplan initial befüllen
# ----------------------------
if st.session_state.plan is None:
    meals = get_meals()
    st.session_state.plan = {
        day: (meals and random.choice(meals)["id"]) or None
        for day in DAYS[lang]
    }

# ----------------------------
# 7. UI Helper-Funktionen
# ----------------------------
def reroll_day(day):
    meals = get_meals()
    cur = st.session_state.plan[day]
    opts = [m for m in meals if m["id"] != cur]
    if opts:
        st.session_state.plan[day] = random.choice(opts)["id"]
        st.experimental_rerun()

def reroll_week():
    meals = get_meals()
    st.session_state.plan = {
        day: (meals and random.choice(meals)["id"]) or None
        for day in DAYS[lang]
    }
    st.experimental_rerun()

def show_detail(mid):
    st.session_state.detail = mid
    st.experimental_rerun()

def refresh_after_delete(mid):
    delete_meal(mid)
    st.experimental_rerun()

# ----------------------------
# 8. Ansicht: Wochenplan
# ----------------------------
if st.session_state.view == "plan":
    st.title("Weekly Meal Planner" if lang=="EN" else "🗓️ Wochen-Mahlzeiten-Planer")
    st.markdown(f"## {('Your Weekly Plan','Dein Wochenplan')[lang=='DE']}")

    cols = st.columns(7)
    for i, day in enumerate(DAYS[lang]):
        with cols[i]:
            st.markdown(f"**{day}**")
            mid = st.session_state.plan[day]
            meal, _ = get_meal(mid)
            if meal:
                col = CATEGORY_COLORS[meal["category"]]
                st.markdown(f"<div style='background:{col};padding:4px;border-radius:4px;'>", unsafe_allow_html=True)
                st.write(meal["name"])
                disp_cat = DISPLAY_CATEGORIES[lang][INTERNAL_CATEGORIES.index(meal["category"])]
                st.caption(disp_cat)
                if st.button("ℹ️", key=f"info_{day}"):
                    show_detail(mid)
                if st.button("🔄", key=f"roll_{day}"):
                    reroll_day(day)
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div style='color:#999'>–</div>", unsafe_allow_html=True)

    if st.button("🔄 Reroll entire week"):
        reroll_week()

# ----------------------------
# 9. Ansicht: Manage Meals
# ----------------------------
elif st.session_state.view == "manage":
    st.title("Manage Meals" if lang=="EN" else "🍽️ Mahlzeiten verwalten")
    st.markdown("Add, edit or delete meals." if lang=="EN" else "Neue Gerichte anlegen, bearbeiten oder löschen.")

    with st.expander("➕ Add New Meal" if lang=="EN" else "➕ Neue Mahlzeit"):
        with st.form("form_add"):
            name = st.text_input("Meal name" if lang=="EN" else "Gericht")
            disp = st.selectbox("Category" if lang=="EN" else "Kategorie", DISPLAY_CATEGORIES[lang])
            cat = INTERNAL_CATEGORIES[DISPLAY_CATEGORIES[lang].index(disp)]
            recipe = st.text_area("Recipe" if lang=="EN" else "Rezept")
            ings = st.text_input("Ingredients (comma-separated)" if lang=="EN" else "Zutaten (Komma)")
            if st.form_submit_button("Create" if lang=="EN" else "Anlegen"):
                if name:
                    add_meal(name, cat, recipe, ings.split(","))
                    st.success("Meal saved!" if lang=="EN" else "Mahlzeit gespeichert!")
                    st.experimental_rerun()

    meals = get_meals()
    for cat in INTERNAL_CATEGORIES:
        disp_cat = DISPLAY_CATEGORIES[lang][INTERNAL_CATEGORIES.index(cat)]
        color = CATEGORY_COLORS[cat]
        st.markdown(f"### <span style='color:{color}'>{disp_cat}</span>", unsafe_allow_html=True)
        cols = st.columns(4)
        items = [m for m in meals if m["category"]==cat]
        for idx, m in enumerate(items):
            with cols[idx%4]:
                st.markdown(f"<div style='background:{color};padding:4px;border-radius:4px;'>",
                            unsafe_allow_html=True)
                st.write(m["name"])
                if st.button("ℹ️", key=f"mi_{m['id']}"):
                    show_detail(m["id"])
                if st.button("🗑️", key=f"md_{m['id']}"):
                    refresh_after_delete(m["id"])
                st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------
# 10. Ansicht: Detail
# ----------------------------
if st.session_state.detail:
    meal, ingredients = get_meal(st.session_state.detail)
    if meal:
        st.markdown("---")
        disp_cat = DISPLAY_CATEGORIES[lang][INTERNAL_CATEGORIES.index(meal["category"])]
        col = CATEGORY_COLORS[meal["category"]]
        st.markdown(f"<h3 style='background:{col};padding:6px;border-radius:4px;color:#fff;'>"
                    f"{meal['name']} ({disp_cat})</h3>", unsafe_allow_html=True)

        st.markdown("#### Ingredients" if lang=="EN" else "#### Zutaten")
        for ing in ingredients:
            c1, c2 = st.columns([4,1])
            c1.write(ing["name"])
            if c2.button("🗑️", key=f"di_{ing['id']}"):
                delete_ingredient(ing["id"])
                st.experimental_rerun()

        new_ing = st.text_input("➕ New ingredient" if lang=="EN" else "➕ Neue Zutat", key="new_ing")
        if st.button("➕ Add" if lang=="EN" else "➕ Hinzufügen"):
            if new_ing.strip():
                add_ingredient(meal["id"], new_ing.strip())
                st.experimental_rerun()

        st.markdown("#### Recipe" if lang=="EN" else "#### Rezept")
        txt = st.text_area("Edit recipe" if lang=="EN" else "Rezept bearbeiten",
                           meal["recipe"] or "", key="rtext")
        if st.button("💾 Save" if lang=="EN" else "💾 Speichern"):
            update_recipe(meal["id"], txt)
            st.success("Recipe saved!" if lang=="EN" else "Rezept gespeichert!")

        c1, c2 = st.columns(2)
        with c1:
            if st.button("🗑️ Delete" if lang=="EN" else "🗑️ Löschen"):
                delete_meal(meal["id"])
                st.experimental_rerun()
        with c2:
            if st.button("⬅️ Back" if lang=="EN" else "⬅️ Zurück"):
                st.session_state.detail = None
                st.experimental_rerun()
    else:
        st.error("This meal no longer exists." if lang=="EN" else "Dieses Gericht existiert nicht mehr.")
        if st.button("⬅️ Back to plan" if lang=="EN" else "⬅️ Zurück zum Plan"):
            st.session_state.detail = None
            st.experimental_rerun()
