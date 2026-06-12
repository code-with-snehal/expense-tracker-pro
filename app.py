import streamlit as st
import pandas as pd
import os
from datetime import date

st.set_page_config(page_title="Expense Tracker Pro", layout="wide", page_icon="💰")

# ---------- FILES ----------
USER_FILE = "users.csv"
DATA_FOLDER = "user_data"
os.makedirs(DATA_FOLDER, exist_ok=True)

# ---------- USER FUNCTIONS ----------
def load_users():
    if os.path.exists(USER_FILE):
        return pd.read_csv(USER_FILE)
    else:
        df = pd.DataFrame({"username": ["Snehal"], "password": ["snehal123"]})
        df.to_csv(USER_FILE, index=False)
        return df

def save_user(username, password):
    df = load_users()
    new_user = pd.DataFrame({"username": [username], "password": [password]})
    df = pd.concat([df, new_user], ignore_index=True)
    df.to_csv(USER_FILE, index=False)

# ---------- EXPENSE FUNCTIONS ----------
def get_user_file(username):
    return os.path.join(DATA_FOLDER, f"expenses_{username}.csv")

def load_expenses(username):
    file = get_user_file(username)
    if os.path.exists(file):
        return pd.read_csv(file)
    else:
        return pd.DataFrame(columns=["Date", "Category", "Amount", "Note"])

def save_expenses(username, df):
    file = get_user_file(username)
    df.to_csv(file, index=False)

# ---------- SESSION STATE ----------
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ""

# ---------- LOGIN / SIGNUP PAGE ----------
if not st.session_state.logged_in:
    st.title("💰 Expense Tracker Pro")
    st.markdown("### Apne kharche track karo - 100% Private & Secure")

    tab1, tab2 = st.tabs(["🔑 Login", "📝 Sign Up"])

    # LOGIN TAB
    with tab1:
        st.subheader("Login Karo")
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")

        if st.button("Login", use_container_width=True):
            users = load_users()
            if username in users['username'].values:
                user_pass = users[users['username'] == username]['password'].values[0]
                if user_pass == password:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.rerun()
                else:
                    st.error("❌ Galat Password!")
            else:
                st.error("❌ User nahi mila! Pehle Sign Up karo")

    # SIGN UP TAB
    with tab2:
        st.subheader("Naya Account Banao - 30 sec mein")
        new_user = st.text_input("Username Chuno", key="signup_user")
        new_pass = st.text_input("Password Chuno", type="password", key="signup_pass")
        confirm_pass = st.text_input("Password Dobara Daalo", type="password", key="confirm_pass")

        if st.button("Sign Up", use_container_width=True):
            if new_user == "" or new_pass == "":
                st.warning("⚠️ Username aur Password khali nahi ho sakta")
            elif len(new_pass) < 4:
                st.warning("⚠️ Password kam se kam 4 digit ka rakho")
            elif new_pass!= confirm_pass:
                st.error("❌ Password match nahi kar raha")
            else:
                users = load_users()
                if new_user in users['username'].values:
                    st.error("❌ Ye username already liya hua hai. Dusra chuno")
                else:
                    save_user(new_user, new_pass)
                    st.success("✅ Account ban gaya! Ab Login tab se login karo")
                    st.balloons()

# ---------- MAIN APP AFTER LOGIN ----------
else:
    # HEADER + LOGOUT
    col1, col2 = st.columns([4,1])
    with col1:
        st.title(f"Welcome, {st.session_state.username} 👋")
    with col2:
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.rerun()

    st.markdown("---")

    # LOAD USER DATA
    df = load_expenses(st.session_state.username)

    # ---------- ADD EXPENSE ----------
    st.subheader("➕ Naya Kharcha Add Karo")
    with st.form("expense_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            exp_date = st.date_input("Date", value=date.today())
        with col2:
            category = st.selectbox("Category", ["Khana", "Travel", "Shopping", "Bills", "Recharge", "Dost", "Other"])
        with col3:
            amount = st.number_input("Amount ₹", min_value=1, step=1)

        note = st.text_input("Note - Kis cheez ka kharcha?")
        submitted = st.form_submit_button("💾 Save Karo", use_container_width=True)

        if submitted:
            new_row = pd.DataFrame({
                "Date": [exp_date],
                "Category": [category],
                "Amount": [amount],
                "Note": [note]
            })
            df = pd.concat([df, new_row], ignore_index=True)
            save_expenses(st.session_state.username, df)
            st.success("✅ Kharcha save ho gaya!")
            st.rerun()

    st.markdown("---")

    # ---------- SHOW DATA ----------
    st.subheader("📊 Tere Saare Kharche")

    if df.empty:
        st.info("Abhi tak koi kharcha add nahi kiya. Upar se add kar 👆")
    else:
        # Total
        total = df["Amount"].sum()
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Kharcha", f"₹ {total}")
        col2.metric("Total Entries", len(df))
        col3.metric("Avg Kharcha", f"₹ {round(total/len(df), 2)}")

        # Table
        st.dataframe(df.sort_values("Date", ascending=False), use_container_width=True, hide_index=True)

        # Category Chart
        st.subheader("📈 Category Wise Kharcha")
        cat_total = df.groupby("Category")["Amount"].sum().sort_values(ascending=False)
        st.bar_chart(cat_total)

        # Delete Option
        st.subheader("🗑️ Kharcha Delete Karo")
        if len(df) > 0:
            delete_index = st.selectbox("Kaunsa row delete karna hai?", df.index,
                                       format_func=lambda x: f"{df.loc[x, 'Date']} - {df.loc[x, 'Category']} - ₹{df.loc[x, 'Amount']}")
            if st.button("Delete Selected Row", type="primary"):
                df = df.drop(delete_index).reset_index(drop=True)
                save_expenses(st.session_state.username, df)
                st.success("Row delete ho gaya!")
                st.rerun()

    # ---------- FOOTER ----------
    st.markdown("---")
    st.markdown("**Made with ❤️ by Snehal Mahure** | Har user ka data 100% private & alag save hota hai 🔒")
