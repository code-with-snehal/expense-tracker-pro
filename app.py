import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Expense Tracker Pro", page_icon="💰", layout="centered")

st.title("💸 Expense Tracker Pro")
st.caption("Apna paisa track kar, warna paisa tujhe track kar lega")

if 'expenses' not in st.session_state:
    st.session_state.expenses = pd.DataFrame(columns=['Date', 'Category', 'Amount', 'Note'])

st.header("➕ Naya Kharcha Jodo")
col1, col2 = st.columns(2)
with col1:
    date = st.date_input("Date", datetime.now())
    category = st.selectbox("Category", ['🍕 Khana', '🚗 Travel', '🛍️ Shopping', '📱 Bills', '🎬 Entertainment', '💊 Health', '📚 Education', 'Other'])
with col2:
    amount = st.number_input("Amount ₹", min_value=1, step=10)
    note = st.text_input("Note", placeholder="Kis cheez pe udaye?")

if st.button("Kharcha Add Karo", type="primary", use_container_width=True):
    new_expense = pd.DataFrame([[date, category, amount, note]], columns=['Date', 'Category', 'Amount', 'Note'])
    st.session_state.expenses = pd.concat([st.session_state.expenses, new_expense], ignore_index=True)
    st.success("Kharcha add ho gaya bhai!")
    st.balloons()

if not st.session_state.expenses.empty:
    st.header("📊 Tera Kharcha Analysis")
    
    df = st.session_state.expenses
    df['Date'] = pd.to_datetime(df['Date'])
    df['Month'] = df['Date'].dt.strftime('%B %Y')
    
    total = df['Amount'].sum()
    this_month = df[df['Month'] == datetime.now().strftime('%B %Y')]['Amount'].sum()
    
    col1, col2, col3 = st.columns(3)
    col1.metric("💰 Total Kharcha", f"₹{total:,.0f}")
    col2.metric("📅 Is Mahine", f"₹{this_month:,.0f}")
    col3.metric("🧾 Total Entries", len(df))

    st.subheader("Kaha Udd Gaya Paisa?")
    fig = px.pie(df, values='Amount', names='Category', hole=0.4, 
                 color_discrete_sequence=px.colors.sequential.RdBu)
    fig.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Mahine Wise Kharcha")
    monthly = df.groupby('Month')['Amount'].sum().reset_index()
    fig2 = px.bar(monthly, x='Month', y='Amount', text_auto='.2s',
                  color='Amount', color_continuous_scale='Blues')
    st.plotly_chart(fig2, use_container_width=True)

    st.header("📋 Saare Kharche")
    st.dataframe(df.sort_values('Date', ascending=False), use_container_width=True, hide_index=True)
    
    if st.button("🗑️ Saara Data Delete Karo", use_container_width=True):
        st.session_state.expenses = pd.DataFrame(columns=['Date', 'Category', 'Amount', 'Note'])
        st.rerun()
    
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 CSV Download Karo", csv, "expenses.csv", "text/csv", use_container_width=True)

else:
    st.info("Abhi tak koi kharcha nahi joda. Upar se start kar 👆")

st.divider()
st.caption("Made with ❤️ by Snehal | Data browser mein save rahega jab tak tab band na ho")
