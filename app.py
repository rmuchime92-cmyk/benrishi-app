import streamlit as st
import pandas as pd
import random

# --- 1. スマホ画面用の基本設定とデザイン調整 ---
st.set_page_config(
    page_title="弁理士 一問一答",
    page_icon="⚖️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# スマホで親指操作しやすくするためのデザイン（CSS）
st.markdown("""
<style>
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 4rem !important;
    }
    header {visibility: hidden;}
    footer {visibility: hidden;}
    /* ボタンを大きく・押しやすく */
    div.stButton > button {
        width: 100%;
        height: 3.8rem;
        font-size: 1.2rem !important;
        font-weight: bold;
        border-radius: 12px;
        margin-bottom: 0.5rem;
    }
    /* 問題文のカードデザイン */
    .question-box {
        background-color: #f8f9fa;
        padding: 1.2rem;
        border-radius: 12px;
        border-left: 5px solid #1f77b4;
        font-size: 1.1rem;
        line-height: 1.6;
        margin-bottom: 1.2rem;
        color: #1e1e1e;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. Googleスプレッドシートからデータを読み込む ---
# 先ほど自動作成したスプレッドシートの専用読み込みURLです
CSV_URL = "https://docs.google.com/spreadsheets/d/1PzRg1YruyR-7tRcOs289Zob1g9diKQxZFlsEnoxiqb0/export?format=csv"

@st.cache_data(ttl=60) # 60秒ごとに最新のスプレッドシートを自動反映
def load_data():
    df = pd.read_csv(CSV_URL)
    return df.dropna(subset=["問題文"])

try:
    df = load_data()
except Exception as e:
    st.error("スプレッドシートの読み込みに失敗しました。スプレッドシートの共有設定が「リンクを知っている全員」になっているか確認してください。")
    st.stop()

# --- 3. 出題の順番や状態の管理 ---
if "q_index" not in st.session_state:
    st.session_state.q_index = 0
if "answered" not in st.session_state:
    st.session_state.answered = False
if "user_choice" not in st.session_state:
    st.session_state.user_choice = None
if "score" not in st.session_state:
    st.session_state.score = {"correct": 0, "total": 0}

# サイドバー（メニュー）にシャッフルボタンや再読み込みボタンを配置
with st.sidebar:
    st.header("⚙️ メニュー")
    if st.button("🔄 最新のスプレッドシートを再読込"):
        st.cache_data.clear()
        st.rerun()
    
    # 科目フィルタ
    subjects = ["すべて"] + list(df["科目"].unique())
    selected_subject = st.selectbox("科目で絞り込む", subjects)

if selected_subject != "すべて":
    df = df[df["科目"] == selected_subject].reset_index(drop=True)

total_q = len(df)
if total_q == 0:
    st.warning("問題データがありません。")
    st.stop()

# インデックスが範囲外にならないよう調整
current_idx = st.session_state.q_index % total_q
row = df.iloc[current_idx]

# --- 4. アプリのメイン画面表示 ---
st.caption(f"📊 正解数: {st.session_state.score['correct']} / {st.session_state.score['total']} 問  ｜  全 {total_q} 問中 {current_idx + 1} 問目")
st.subheader(f"【{row['科目']}】 {row['年度・問題番号']}（枝{row['枝番']}）")

# 問題文の表示
st.markdown(f"<div class='question-box'>{row['問題文']}</div>", unsafe_allow_html=True)

# ◯ × ボタン（横並び）
col1, col2 = st.columns(2)
with col1:
    if st.button("◯ 正しい", disabled=st.session_state.answered):
        st.session_state.answered = True
        st.session_state.user_choice = "◯"
        st.session_state.score["total"] += 1
        if row["正解"] == "◯":
            st.session_state.score["correct"] += 1
        st.rerun()

with col2:
    if st.button("× 誤り", disabled=st.session_state.answered):
        st.session_state.answered = True
        st.session_state.user_choice = "×"
        st.session_state.score["total"] += 1
        if row["正解"] == "×":
            st.session_state.score["correct"] += 1
        st.rerun()

# --- 5. 回答後の正誤判定と解説表示 ---
if st.session_state.answered:
    is_correct = (st.session_state.user_choice == row["正解"])
    if is_correct:
        st.success(f"⭕ **大正解！** （正解：{row['正解']}）")
    else:
        st.error(f"❌ **不正解...** （正解：{row['正解']}）")
    
    st.info(f"💡 **解説**\n\n{row['解説']}")

    # 次の問題へ進むボタン
    col_next1, col_next2 = st.columns(2)
    with col_next1:
        if st.button("➡️ 次の問題へ"):
            st.session_state.q_index += 1
            st.session_state.answered = False
            st.session_state.user_choice = None
            st.rerun()
    with col_next2:
        if st.button("🎲 ランダムに出題"):
            st.session_state.q_index = random.randint(0, total_q - 1)
            st.session_state.answered = False
            st.session_state.user_choice = None
            st.rerun()
