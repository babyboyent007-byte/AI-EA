import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import os
from datetime import datetime
import time

# Page configuration
st.set_page_config(page_title='AI-EA LIVE MONITOR', layout='wide')

DB_PATH = 'AI-EA/database/market.db'

def load_data(query):
    if not os.path.exists(DB_PATH):
        return pd.DataFrame()
    try:
        # Connect with timeout to handle concurrency
        conn = sqlite3.connect(DB_PATH, timeout=10)
        # Enable WAL mode for safer concurrent reads/writes
        conn.execute('PRAGMA journal_mode=WAL;')
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f'Database Error: {e}')
        return pd.DataFrame()

# Sidebar status with refresh toggle
st.sidebar.header('System Control')
refresh_rate = st.sidebar.slider('Refresh rate (seconds)', 5, 60, 15)

# Main Dashboard Header
st.title('☑ AI-EA Performance Monitor')
st.caption(f"Last Refresh: {datetime.now().strftime('%H:%M:%S')}")

# Metrics & Visuals
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader('Equity Curve')
    trades_df = load_data('SELECT time, price, lots FROM trades ORDER BY time ASC')
    if not trades_df.empty:
        trades_df['cumulative_pnl'] = (trades_df['price'].pct_change().fillna(0) * 100000).cumsum()
        fig = px.line(trades_df, x='time', y='cumulative_pnl', 
                     title='Growth Performance', markers=True)
        fig.update_layout(template='plotly_dark')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info('Waiting for trade data synchronization...')

with col2:
    st.subheader('Model Consensus')
    pred_df = load_data('SELECT * FROM predictions ORDER BY id DESC LIMIT 1')
    if not pred_df.empty:
        st.metric('Ensemble Score', f"{pred_df['ensemble_score'].iloc[0]:.1f}%")
        st.write(f"XGB Prob: {pred_df['xgb_prob'].iloc[0]:.2%}")
        st.write(f"LGBM Prob: {pred_df['lgbm_prob'].iloc[0]:.2%}")
        st.progress(pred_df['ensemble_score'].iloc[0] / 100)
    else:
        st.info('No active predictions.')

st.subheader('Recent Trade Audit')
st.dataframe(load_data('SELECT * FROM trades ORDER BY time DESC LIMIT 20'), use_container_width=True)

# Auto-refresh mechanism
time.sleep(refresh_rate)
st.rerun()