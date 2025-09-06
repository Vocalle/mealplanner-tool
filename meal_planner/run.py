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
        )""")
    c.execute("""
        CREATE TABLE IF NOT EXISTS ingredient (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            meal_id INTEGER,
            FOREIGN KEY(meal_id) REFERENCES meal(id) ON DELETE CASCADE
        )""")
    conn.commit()

    # Beispiel-Datensatz
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


# ----------------------------
# 2. Sprach-abhängige Werte
# ----------------------------
if "lang" not in st.session_state:
    st.session_state.lang = "DE"

# Wochentage
DAYS = {
    "DE": ["Montag","Dienstag","Mittwoch","Donnerstag","Freitag","Samstag","Sonntag"],
    "EN": ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
}

# Kategorien
CATEGORIES = {
    "DE": ["Vegan","Vegetarisch","Fleisch"],
    "EN": ["Vegan","Vegetarian","Meat"]
}

# Farben pro Kategorie (unabhängig von Sprache)
CATEGORY_COLORS = {
    "Vegan":      "#27ae60",
    "Vegetarisch":"#f1c40f",
    "Fleisch":    "#c0392b"
}


# ----------------------------
# 3. DB-Funktionen
# ----------------------------
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
        cur.execute(
            "INSERT INTO meal (name, category, recipe) VALUES (?, ?, ?)",
            (name, category, recipe)
        )
        meal_id = cur.lastrowid
        for ing in ingredients:
            if ing.strip():
                cur.execute(
                    "INSERT INTO ingredient (name, meal_id) VALUES (?, ?)",
                    (ing.strip(), meal_id)
                )
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
        conn.execute(
            "INSERT INTO ingredient (name, meal_id) VALUES (?, ?)",
            (name, meal_id)
        )
        conn.commit()

def delete_ingredient(ing_id):
    with get_db() as conn:
        conn.execute("DELETE FROM ingredient WHERE id=?", (ing_id,))
        conn.commit()


# ----------------------------
# 4. Session State Defaults
# ----------------------------
for key, default in [
    ("view",      "plan"),
    ("plan",      None),
    ("detail",    None),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# initialer Sidebar-Sprachwechsel
lang = st.sidebar.radio(
    "Sprache" if st.session_state.lang=="DE" else "Language",
    options=["DE","EN"],
    index=0 if st.session_state.lang=="DE" else 1,
    key="lang"
)


# ----------------------------
# 5. Wochenplan befüllen
# ----------------------------
if st.session_state.plan is None:
    meals = get_meals()
    st.session_state.plan = {
        tag: (meals and random.choice(meals)["id"]) or None
        for tag in DAYS[lang]
    }


# ----------------------------
# 6. Style
# ----------------------------
st.markdown("""
<style>
.meal-card {
  color: #fff;
  padding: 0.5rem;
  margin-bottom: 0.5rem;
  border-radius: 6px;
}
.stButton > button {
  padding: 0.2rem 0.4rem;
  margin-right: 0.2rem;
  font-size: 0.8rem;
}
</style>
""", unsafe_allow_html=True)


# ----------------------------
# 7. Navigation
# ----------------------------
pages = {
    "🗓️ Wochenplan" if lang=="DE" else "🗓️ Weekly Plan": "plan",
    "Mahlzeiten verwalten" if lang=="DE" else "Manage Meals": "manage"
}
choice = st.sidebar.radio("", list(pages.keys()))
st.session_state.view = pages[choice]


# ----------------------------
# 8. Hilfsfunktionen UI
# ----------------------------
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


# ----------------------------
# 9. View: Wochenplan
# ----------------------------
if st.session_state.view == "plan":
    st.title("🗓️ Wochen-Mahlzeiten-Planer" if lang=="DE" else "🗓️ Weekly Meal Planner")
    st.markdown("## Dein Wochenplan" if lang=="DE" else "## Your Weekly Plan")

    cols = st.columns(7)
    for i, tag in enumerate(DAYS[lang]):
        with cols[i]:
            st.markdown(f"**{tag}**")
            meal_id = st.session_state.plan.get(tag)
            meal, _ = get_meal(meal_id)
            if meal:
                color = CATEGORY_COLORS.get(meal["category"], "#333")
                st.markdown(f"<div class='meal-card' style='background:{color}'>", unsafe_allow_html=True)
                st.write(meal["name"])
                st.button("ℹ️" if lang=="DE" else "ℹ️", key=f"detail_{tag}", on_click=show_meal_detail, args=(meal_id,))
                st.button("🔄" if lang=="DE" else "🔄", key=f"reroll_{tag}", help="Neu würfeln" if lang=="DE" else "Reroll", on_click=reroll_day, args=(tag,))
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='meal-card' style='background:#555'><i>–</i></div>", unsafe_allow_html=True)

    if st.button("Woche komplett neu würfeln" if lang=="DE" else "Reroll entire week"):
        meals = get_meals()
        st.session_state.plan = {tag: (meals and random.choice(meals)["id"]) or None for tag in DAYS[lang]}
        st.rerun()

    st.divider()
    st.markdown("**Tipp:** Neue Gerichte kannst du im Menü 'Mahlzeiten verwalten' anlegen." if lang=="DE" else "**Tip:** You can add new meals under 'Manage Meals'.")


# ----------------------------
# 10. View: Manage Meals
# ----------------------------
elif st.session_state.view == "manage":
    st.title("🍽️ Mahlzeiten verwalten" if lang=="DE" else "🍽️ Manage Meals")
    st.markdown(
        "Lege neue Gerichte an, bearbeite oder lösche bestehende."
        if lang=="DE" else
        "Add, edit or delete meals."
    )

    with st.expander("➕ Neue Mahlzeit hinzufügen" if lang=="DE" else "➕ Add New Meal"):
        with st.form("add_meal_form"):
            name        = st.text_input("Gericht" if lang=="DE" else "Meal name")
            category    = st.selectbox(
                             "Kategorie" if lang=="DE" else "Category",
                             options=CATEGORIES[lang]
                         )
            recipe      = st.text_area("Rezept" if lang=="DE" else "Recipe")
            ingredients = st.text_input("Zutaten (Kommagetrennt)" if lang=="DE" else "Ingredients (comma separated)")
            submitted   = st.form_submit_button("✔️ Anlegen" if lang=="DE" else "✔️ Create")
            if submitted and name and category:
                add_meal(name, category, recipe, ingredients.split(","))
                st.success("Mahlzeit gespeichert!" if lang=="DE" else "Meal saved!")
                st.rerun()

    meals = get_meals()
    for cat in CATEGORIES[lang]:
        color = CATEGORY_COLORS.get(cat, "#333")
        st.markdown(f"<h3 style='color:{color}'>{cat}</h3>", unsafe_allow_html=True)
        cols = st.columns(4)
        cat_meals = [m for m in meals if m["category"] == cat]
        for i, meal in enumerate(cat_meals):
            with cols[i % 4]:
                st.markdown(f"<div class='meal-card' style='background:{color}'>", unsafe_allow_html=True)
                st.markdown(f"**{meal['name']}**", unsafe_allow_html=True)
                st.button("ℹ️" if lang=="DE" else "ℹ️", key=f"detail_manage_{meal['id']}", on_click=show_meal_detail, args=(meal['id'],))
                st.button("🗑️ Löschen" if lang=="DE" else "🗑️ Delete", key=f"del_manage_{meal['id']}", on_click=delete_and_refresh, args=(meal['id'],))
                st.markdown("</div>", unsafe_allow_html=True)


# ----------------------------
# 11. Detail-Ansicht
# ----------------------------
if st.session_state.detail:
    meal, ings = get_meal(st.session_state.detail)
    if meal:
        st.markdown("---")
        color = CATEGORY_COLORS.get(meal["category"], "#333")
        st.markdown(f"<div class='meal-card' style='background:{color}'>", unsafe_allow_html=True)
        st.markdown(f"### {meal['name']} ({meal['category']})")
        st.markdown("</div>")

        st.markdown("#### Zutaten" if lang=="DE" else "#### Ingredients")
        for ing in ings:
            c1, c2 = st.columns([4,1])
            c1.write(ing["name"])
            c2.button("🗑️" if lang=="DE" else "🗑️", key=f"del_ing_{ing['id']}", on_click=delete_ingredient, args=(ing['id'],))

        new_ing = st.text_input("➕ Neue Zutat" if lang=="DE" else "➕ New ingredient")
        if st.button("✔️ Hinzufügen" if lang=="DE" else "✔️ Add"):
            if new_ing.strip():
                add_ingredient(meal["id"], new_ing.strip())
                st.rerun()

        st.markdown("#### Rezept" if lang=="DE" else "#### Recipe")
        recipe = st.text_area(
            "Rezept bearbeiten" if lang=="DE" else "Edit recipe",
            meal["recipe"] or ""
        )
        if st.button("💾 Speichern" if lang=="DE" else "💾 Save"):
            update_recipe(meal["id"], recipe)
            st.success("Rezept gespeichert!" if lang=="DE" else "Recipe saved!")

        c1, c2 = st.columns(2)
        with c1:
            st.button("🗑️ Löschen" if lang=="DE" else "🗑️ Delete", on_click=delete_meal, args=(meal["id"],))
        with c2:
            st.button("⬅️ Zurück" if lang=="DE" else "⬅️ Back", on_click=lambda: st.session_state.update(detail=None))


    else:
        st.error("Dieses Gericht existiert nicht mehr." if lang=="DE" else "This meal no longer exists.")
        st.button("⬅️ Zurück zum Plan" if lang=="DE" else "⬅️ Back to plan", on_click=lambda: st.session_state.update(detail=None))
