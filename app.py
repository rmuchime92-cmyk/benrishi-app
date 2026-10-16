import streamlit as st
import pandas as pd
import random
import json
import os
import re
from datetime import datetime, timedelta

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

    /* 🎯 1日10問 目標ゲージカード */
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
    .goal-sub {
        font-size: 0.78rem;
        font-weight: 700;
        color: #2563EB;
    }
    .goal-sub-done {
        font-size: 0.78rem;
        font-weight: 800;
        color: #10B981;
    }
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
        transition: width 0.3s ease;
    }
    .progress-fill-done {
        height: 100%;
        background: linear-gradient(90deg, #10B981, #34D399);
        border-radius: 999px;
        transition: width 0.3s ease;
    }

    /* 🗺️ 条文別マスターヒートマップ */
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
    .heatmap-legend {
        font-size: 0.7rem;
        font-weight: 600;
        color: #6B7280;
    }
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
        word-break: keep-all;
    }
    .hm-sub {
        font-size: 0.65rem;
        font-weight: 600;
        opacity: 0.92;
        display: block;
        margin-top: 2px;
    }
    .hm-green { background-color: #10B981; color: #FFFFFF; }
    .hm-yellow { background-color: #F59E0B; color: #FFFFFF; }
    .hm-red { background-color: #EF4444; color: #FFFFFF; }

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
        margin-bottom: 1.0rem;
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
        font-size: 0.85rem;
        margin-top: 0.8rem;
        margin-bottom: 0.8rem;
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
        border-radius: 20px;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.04);
        font-size: 1.05rem;
        line-height: 1.7;
        color: #1A1D26;
        margin-bottom: 1.2rem;
        font-weight: 500;
        width: 100%;
        box-sizing: border-box;
        word-wrap: break-word;
    }

    /* ==========================================================
       スマホの横幅を3つのボタン（◯・？・×）でめいっぱい使う設定
       ========================================================== */
    div[data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        width: 100% !important;
        gap: 10px !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    div[data-testid="stHorizontalBlock"] > div[data-testid="column"],
    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
        flex: 1 1 0% !important;
        width: 33.33% !important;
        min-width: 0 !important;
        padding: 0 !important;
    }
    div[data-testid="stHorizontalBlock"] button {
        width: 100% !important;
        min-width: 100% !important;
        height: 4.8rem !important;
        border-radius: 18px !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        text-align: center !important;
        padding: 0 !important;
        margin: 0 !important;
    }
    div[data-testid="stHorizontalBlock"] button p {
        font-size: 2rem !important;
        font-weight: 900 !important;
        margin: 0 !important;
        line-height: 1 !important;
    }

    /* 左：正しいボタン（青背景に白丸） */
    div[data-testid="stHorizontalBlock"] > div:nth-child(1) button {
        background-color: #2563EB !important;
        color: #FFFFFF !important;
        box-shadow: 0 5px 15px rgba(37, 99, 235, 0.28) !important;
    }
    /* 中央：わからないボタン（白背景に黒の？） */
    div[data-testid="stHorizontalBlock"] > div:nth-child(2) button {
        background-color: #FFFFFF !important;
        color: #111827 !important;
        border: 2px solid #D1D5DB !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05) !important;
    }
    /* 右：誤りボタン（赤背景に白の×） */
    div[data-testid="stHorizontalBlock"] > div:nth-child(3) button {
        background-color: #DC2626 !important;
        color: #FFFFFF !important;
        box-shadow: 0 5px 15px rgba(220, 38, 38, 0.28) !important;
    }

    /* 解説カード */
    .explanation-card {
        background-color: #FFFFFF;
        padding: 1.2rem;
        border-radius: 18px;
        border-left: 6px solid #2563EB;
        box-shadow: 0 4px 15px rgba(0,0,0,0.03);
        font-size: 0.95rem;
        line-height: 1.65;
        color: #374151;
        margin-top: 0.8rem;
        margin-bottom: 1.2rem;
        width: 100%;
        box-sizing: border-box;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. スプレッドシートから問題データを読み込む ---
CSV_URL = "https://docs.google.com/spreadsheets/d/1PzRg1YruyR-7tRcOs289Zob1g9diKQxZFlsEnoxiqb0/export?format=csv"

@st.cache_data(ttl=60)
def load_questions():
    df = pd.read_csv(CSV_URL)
    df = df.dropna(subset=["問題文"]).reset_index(drop=True)
    df["qid"] = df["科目"].astype(str) + "_" + df["年度・問題番号"].astype(str) + "_" + df["枝番"].astype(str)
    return df

try:
    df_all = load_questions()
except Exception:
    st.error("スプレッドシートの読み込みに失敗しました。共有設定を確認してください。")
    st.stop()

# --- 4. 学習履歴（正答率・苦手リスト）の保存・読込システム ---
STATS_FILE = "user_study_stats.json"
DAILY_GOAL = 10  # 🎯 1日の目標問題数

def load_stats():
    if os.path.exists(STATS_FILE):
        try:
            with open(STATS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"questions": {}, "daily": {}}

def save_stats(stats_data):
    try:
        with open(STATS_FILE, "w", encoding="utf-8") as f:
            json.dump(stats_data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

if "stats" not in st.session_state:
    st.session_state.stats = load_stats()
if "page" not in st.session_state:
    st.session_state.page = "home"  # "home", "auto", "weak"
if "current_qid" not in st.session_state:
    st.session_state.current_qid = None
if "answered" not in st.session_state:
    st.session_state.answered = False
if "user_choice" not in st.session_state:
    st.session_state.user_choice = None
if "selected_subject" not in st.session_state:
    st.session_state.selected_subject = "すべての科目"
if "just_hit_goal" not in st.session_state:
    st.session_state.just_hit_goal = False

# --- 5. ストリーク・累計回答数・条文抽出の集計ロジック ---
def calculate_streak(daily_dict):
    """連続学習日数（ストリーク）を計算"""
    today = datetime.now().date()
    streak = 0
    check_date = today

    # 今日まだ解いていなくても、昨日解いていればストリーク継続中として表示
    if daily_dict.get(today.strftime("%Y-%m-%d"), 0) == 0:
        check_date = today - timedelta(days=1)

    while True:
        d_str = check_date.strftime("%Y-%m-%d")
        if daily_dict.get(d_str, 0) > 0:
            streak += 1
            check_date -= timedelta(days=1)
        else:
            break
    return streak

def calculate_total_answers(stats_data):
    """累計回答数を計算（dailyの合計とquestionsの合計の大きい方を採用）"""
    daily_sum = sum(stats_data.get("daily", {}).values())
    q_sum = sum(
        q.get("correct", 0) + q.get("wrong", 0)
        for q in stats_data.get("questions", {}).values()
    )
    return max(daily_sum
