import streamlit as st
import pandas as pd
import random
import json
import os
from datetime import datetime

# --- 1. ページ基本設定 ---
st.set_page_config(
    page_title="Benrishi X",
    page_icon="⚖️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- 2. スマホ画面幅100%最適化 ＆ Memora X 風CSS ---
st.markdown("""
<style>
    /* スマホでの横スクロール（はみ出し）を完全に防止 */
    html, body, .stApp {
        background-color: #F4F6FA;
        font-family: 'Helvetica Neue', Arial, 'Hiragino Kaku Gothic ProN', 'Hiragino Sans', Meiryo, sans-serif;
        overflow-x: hidden !important;
        max-width: 100vw !important;
    }

    /* スマホ画面の横幅をめいっぱい使う余白設定 */
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

    /* ヘッダータイトル（Memora X風） */
    .app-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.5rem;
        width: 100%;
    }
    .app-title {
        font-size: 1.75rem;
        font-weight: 800;
        color: #1A1D26;
        letter-spacing: -0.5px;
        margin: 0;
    }
    .diamond-badge {
        background-color: #FFFFFF;
        padding: 6px 14px;
        border-radius: 50px;
        box-shadow: 0 3px 10px rgba(0,0,0,0.04);
        font-weight: 700;
        font-size: 0.9rem;
        color: #1A1D26;
    }

    /* すべてのボタンの基本設定（横幅100%強制） */
    .stButton, div[data-testid="stButton"] {
        width: 100% !important;
    }
    div.stButton > button, div[data-testid="stButton"] > button {
        width: 100% !important;
        max-width: 100% !important;
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
        transition: transform 0.1s ease;
        margin-bottom: 0.6rem;
        box-sizing: border-box !important;
    }
    div.stButton > button:active, div[data-testid="stButton"] > button:active {
        transform: scale(0.98);
    }

    /* 苦手問題数の赤字バッジ表示用バー */
    .weak-status-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0 0.4rem;
        margin-top: -0.2rem;
        margin-bottom: 1.2rem;
        font-size: 0.82rem;
        font-weight: 700;
        color: #6B7280;
    }
    .weak-count-red {
        color: #E03131;
        font-weight: 800;
        font-size: 0.95rem;
    }

    /* フッター統計（今日 ◯回答） */
    .today-stats {
        text-align: center;
        color: #5A6275;
        font-weight: 700;
        font-size: 0.9rem;
        margin-top: 1.5rem;
    }

    /* --- 問題画面のカードデザイン --- */
    .q-header-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.6rem;
        gap: 6px;
        flex-wrap: wrap;
    }
    .q-meta-tag {
        font-size: 0.8rem;
        font-weight: 700;
        color: #2B5CE6;
        background: #E8F0FE;
        padding: 4px 10px;
        border-radius: 20px;
    }
    .q-rate-tag {
        font-size: 0.8rem;
        font-weight: 700;
        color: #4B5563;
        background: #FFFFFF;
        padding: 4px 10px;
        border-radius: 20px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.04);
    }
    .question-card {
        background-color: #FFFFFF;
        padding: 1.25rem;
        border-radius: 2
