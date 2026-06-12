import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

st.set_page_config(page_title="Expense Tracker Pro", page_icon="💸", layout="wide")

# YAHAN NAYE USERS ADD KAR SAKTA HAI
USERS = {
    "Snehal": "snehal123",
    "Guest": "guest123"
}

# Login System
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

if not st.session_state.logged_in:
    st.title("🔐 Expense Tracker Pro - Login")
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("### Login Karo")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login_btn = st.button("Login", use_container_width=True, type="primary")

        if login_btn:
            if username in USERS and USERS[username] == password:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("❌ Galat Username ya Password!")
    st.stop()

# User ka data file
DATA_FILE = f"data_{st.session_state.username}.csv"

# Data load karo
if 'expenses' not in st.session_state:
    if os.path.exists(DATA_FILE):
        st.session_state.expenses = pd.read_csv(DATA_FILE)
        st.session_state.expenses['Date'] = pd.to_datetime(st.session_state.expenses['Date'])
    else:
        st.session_state.expenses = pd.DataFrame(columns=['Date', 'Category', 'Amount', 'Note'])

# Sidebar - Logout
with st.sidebar:
    st.markdown(f"### 👋 Hello, {st.session_state.username}")
    st.markdown("---")
    if st.button("🚪 Logout", use_container_width=True):
        for key in st.session_state.keys():
            del st.session_state[key]
        st.rerun()

st.title("💸 Expense Tracker Pro")
st.markdown(f"### Welcome, **{st.session_state.username}**! Apna kharcha track karo")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("➕ Naya Kharcha Add Karo")

    with st.form("expense_form", clear_on_submit=True):
        date = st.date_input("Date", datetime.now())
        category = st.selectbox("Category",
            ['Khana', 'Transport', 'Shopping', 'Bills', 'Entertainment', 'Health', 'Education', 'Other'])
        amount = st.number_input("Amount (₹)", min_value=0.0, step=10.0)
        note = st.text_input("Note", placeholder="Pizza khaya")

        submitted = st.form_submit_button("💰 Kharcha Add Karo", use_container_width=True)

        if submitted:
            if amount <= 0:
                st.warning("Amount 0 se zyada hona chahiye!")
            else:
                new_expense = pd.DataFrame({
                    'Date': [date],
                    'Category': [category],
                    'Amount': [amount],
                    'Note': [note]
                })
                st.session_state.expenses = pd.concat([st.session_state.expenses, new_expense], ignore_index=True)
                st.session_state.expenses.to_csv(DATA_FILE, index=False)
                st.success(f"✅ ₹{amount} ka kharcha save ho gaya!")
                st.rerun()

with col2:
    st.subheader("📊 Quick Stats")
    if not st.session_state.expenses.empty:
        total = st.session_state.expenses['Amount'].sum()
        count = len(st.session_state.expenses)
        avg = st.session_state.expenses['Amount'].mean()

        col_a, col_b = st.columns(2)
        col_a.metric("Total Kharcha", f"₹{total:,.0f}")
        col_b.metric("Total Entries", count)
        st.metric("Average Kharcha", f"₹{avg:,.0f}")
    else:
        st.info("Abhi koi data nahi hai")

if not st.session_state.expenses.empty:
    st.markdown("---")
    st.subheader("📈 Kharcha Analysis")

    col3, col4 = st.columns(2)

    with col3:
        category_sum = st.session_state.expenses.groupby('Category')['Amount'].sum().reset_index()
        fig = px.pie(category_sum, values='Amount', names='Category',
                     title='Category ke Hisaab se Kharcha',
                     hole=0.3)
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        daily = st.session_state.expenses.groupby('Date')['Amount'].sum().reset_index()
        fig2 = px.bar(daily, x='Date', y='Amount', title='Roz ka Kharcha',
                     text_auto='.0f')
        fig2.update_traces(marker_color='#FF4B4B')
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")
    st.subheader("📋 Saare Kharchon ki List")

    col_del1, col_del2 = st.columns([3,1])
    with col_del2:
        if st.button("🗑️ Saara Data Delete Karo", use_container_width=True):
            st.session_state.expenses = pd.DataFrame(columns=['Date', 'Category', 'Amount', 'Note'])
            st.session_state.expenses.to_csv(DATA_FILE, index=False)
            st.success("Saara data delete ho gaya!")
            st.rerun()

    st.dataframe(
        st.session_state.expenses.sort_values('Date', ascending=False),
        use_container_width=True,
        hide_index=True
    )

    csv = st.session_state.expenses.to_csv(index=False).encode('utf-8')
    st.download_button(
        "⬇️ CSV Download Karo",
        csv,
        f"expenses_{st.session_state.username}.csv",
        "text/csv",
        use_container_width=True
    )
else:
    st.info("👆 Upar se pehla kharcha add karo!")

st.markdown("---")
st.markdown("<p style='text-align: center;'>Made with ❤️ by <b>Snehal Mahure</b> | Data permanently save rahega</p>", unsafe_allow_html=True)
