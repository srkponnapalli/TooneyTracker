import streamlit as st
import psycopg2
import pandas as pd
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv("../backend/.env")

# DB Connection
def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

# Data fetchers
def get_transactions():
    conn = get_connection()
    df = pd.read_sql("""
        SELECT 
            t.date,
            t.merchant_name,
            t.raw_name,
            t.amount,
            t.pending,
            t.payment_channel,
            a.name as account_name,
            a.type as account_type
        FROM transactions t
        JOIN accounts a ON t.account_id = a.id
        ORDER BY t.date DESC
    """, conn)
    conn.close()
    return df

def get_monthly_summary():
    conn = get_connection()
    df = pd.read_sql("""
        SELECT 
            DATE_TRUNC('month', date) as month,
            SUM(amount) as total_spent,
            COUNT(*) as transaction_count
        FROM transactions
        WHERE pending = false
        GROUP BY DATE_TRUNC('month', date)
        ORDER BY month DESC
    """, conn)
    conn.close()
    return df

def get_account_balances():
    conn = get_connection()
    df = pd.read_sql("""
        SELECT 
            name,
            type,
            subtype,
            current_balance,
            available_balance
        FROM accounts
        ORDER BY type, name
    """, conn)
    conn.close()
    return df

# UI
st.set_page_config(page_title="TooneyTracker 🍁", layout="wide")
st.title("TooneyTracker 🍁")
st.caption("Your Canadian personal finance dashboard")

# Accounts Overview
st.subheader("Account Balances")
balances = get_account_balances()
st.dataframe(balances, use_container_width=True)

# Monthly Summary
st.subheader("Monthly Spending Summary")
monthly = get_monthly_summary()
if not monthly.empty:
    col1, col2 = st.columns(2)
    with col1:
        st.metric(
            "This Month's Spending",
            f"${monthly.iloc[0]['total_spent']:,.2f}",
            delta=f"{monthly.iloc[0]['transaction_count']} transactions"
        )
    with col2:
        if len(monthly) > 1:
            st.metric(
                "Last Month's Spending",
                f"${monthly.iloc[1]['total_spent']:,.2f}",
                delta=f"{monthly.iloc[1]['transaction_count']} transactions"
            )
    st.bar_chart(monthly.set_index('month')['total_spent'])

# Transactions
st.subheader("Recent Transactions")
df = get_transactions()
if not df.empty:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Transactions", len(df))
    with col2:
        st.metric("Total Spent", f"${df['amount'].sum():,.2f}")
    with col3:
        st.metric("Accounts Connected", df['account_name'].nunique())

    # Filters
    accounts = ["All"] + list(df['account_name'].unique())
    selected_account = st.selectbox("Filter by Account", accounts)
    if selected_account != "All":
        df = df[df['account_name'] == selected_account]

    st.dataframe(df, use_container_width=True)
else:
    st.info("No transactions found. Sync your accounts first.")