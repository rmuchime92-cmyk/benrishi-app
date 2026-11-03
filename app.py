from datetime import datetime, timedelta
import json
import os
import random
import re
import threading  # ⚡ バックグラウンド通信用（待ち時間ゼロ化）
import pandas as pd
import requests
import streamlit as st

# --- 1. ページ基本設定 ---
st.set_page_config(
    page_title="Benrishi X",
    page_icon="⚖️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# --- 2. スマホ画面幅100%最適化 ＆ Memora X 風CSS ---
st.markdown(
    """
<style>
    html, body, .stApp {
        background-color: #F4F6FA;
        font-family: 'Helvetica Neue', Arial, 'Hiragino Kaku Gothic ProN', 'Hiragino Sans', Meiryo, sans-serif;
        overflow-x: hidden !important;
        max-width: 100vw !important;
    }

    .block-container {
        padding-top: 1.2rem !important;
        padding-bottom: 3rem !important;
        padding-left: 0.8rem !important;
        padding-right: 0.8rem !important;
        max-width: 100% !important;
        box-sizing: border-box !important;
    }
    header {visibility: hidden;}
    footer {visibility: hidden;}

    .app-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.6rem;
        width: 100%;
    }
    .app-title {
        font-size: 1.75rem;
        font-weight: 800;
        color: #1A1D26;
        letter-spacing: -0.5px;
        margin: 0;
    }
    .badge-group {
        display: flex;
        gap: 6px;
        align-items: center;
    }
    .stat-pill {
        background-color: #FFFFFF;
        padding: 5px 11px;
        border-radius: 50px;
        box-shadow: 0 3px 10px rgba(0,0,0,0.04);
        font-weight: 800;
        font-size: 0.82rem;
        color: #1A1D26;
        display: flex;
        align-items: center;
        gap: 3px;
    }

    .goal-card {
        background-color: #FFFFFF;
        padding: 0.9rem 1.1rem;
        border-radius: 18px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.03);
        margin-bottom: 0.9rem;
        width: 100%;
        box-sizing: border-box;
    }
    .goal-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.45rem;
        font-size: 0.85rem;
        font-weight: 800;
        color: #1A1D26;
    }
    .goal-sub { font-size: 0.78rem; font-weight: 700; color: #2563EB; }
    .goal-sub-done { font-size: 0.78rem; font-weight: 800; color: #10B981; }
    .progress-track {
        width: 100%;
        height: 10px;
        background-color: #E5E7EB;
        border-radius: 999px;
        overflow: hidden;
    }
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #2563EB, #3B82F6);
        border-radius: 999px;
    }
    .progress-fill-done {
        height: 100%;
        background: linear-gradient(90deg, #10B981, #34D399);
        border-radius: 999px;
    }

    .heatmap-card {
        background-color: #FFFFFF;
        padding: 1.1rem;
        border-radius: 18px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.03);
        margin-top: 0.4rem;
        margin-bottom: 1rem;
        width: 100%;
        box-sizing: border-box;
    }
    .heatmap-title {
        font-size: 0.95rem;
        font-weight: 800;
        color: #1A1D26;
        margin-bottom: 0.7rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .heatmap-legend { font-size: 0.7rem; font-weight: 600; color: #6B7280; }
    .heatmap-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(78px, 1fr));
        gap: 6px;
        width: 100%;
    }
    .hm-tile {
        padding: 7px 4px;
        border-radius: 10px;
        text-align: center;
        font-weight: 800;
        font-size: 0.76rem;
        line-height: 1.25;
        box-shadow: 0 2px 5px rgba(0,0,0,0.06);
    }
    .hm-sub { font-size: 0.65rem; font-weight: 600; opacity: 0.92; display: block; margin-top: 2px; }
    .hm-green { background-color: #10B981; color: #FFFFFF; }
    .hm-yellow { background-color: #F59E0B; color: #FFFFFF; }
    .hm-red { background-color: #EF4444; color: #FFFFFF; }

    .stButton, div[data-testid="stButton"] { width: 100% !important; }
    div.stButton > button, div[data-testid="stButton"] > button {
        width: 100% !important;
        background-color: #FFFFFF;
        color: #1A1D26;
        border: none;
        border-radius: 18px;
        padding: 1.4rem 1.2rem;
        font-size: 1.2rem !important;
        font-weight: 800 !important;
        display: flex;
        justify-content: flex-start;
        align-items: center;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.03);
        margin-bottom: 0.6rem;
    }

    .weak-status-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0 0.4rem;
        margin-top: -0.2rem;
        margin-bottom: 0.8rem;
        font-size: 0.82rem;
        font-weight: 700;
        color: #6B7280;
    }
    .unseen-count-blue { color: #2563EB; font-weight: 800; font-size: 0.92rem; }
    .weak-count-red { color: #E03131; font-weight: 800; font-size: 0.95rem; }
    .today-stats { text-align: center; color: #5A6275; font-weight: 700; font-size: 0.85rem; margin: 0.8rem 0; }

    .q-header-bar {
        display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.6rem; gap: 6px;
    }
    .q-meta-tag { font-size: 0.8rem; font-weight: 700; color: #2B5CE6; background: #E8F0FE; padding: 4px 10px; border-radius: 20px; }
    .q-rate-tag { font-size: 0.8rem; font-weight: 700; color: #4B5563; background: #FFFFFF; padding: 4px 10px; border-radius: 20px; box-shadow: 0 2px 6px rgba(0,0,0,0.04); }
    .question-card {
        background-color: #FFFFFF; padding: 1.25rem; border-radius: 20px; box-shadow
