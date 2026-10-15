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

# --- 2. Memora X 風のスタイリッシュCSS ---
st.markdown("""
<style>
    /* 全体の背景色（淡いブルーグレー）と余白設定 */
    .stApp {
        background-color: #F4F6FA;
        font-family: 'Helvetica Neue', Arial, 'Hiragino Kaku Gothic ProN', 'Hiragino Sans', Meiryo, sans-serif;
    }
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 5rem !important;
        max-width: 480px;
    }
    header {visibility: hidden;}
    footer {visibility: hidden;}

    /* ヘッダータイトル（Memora X風） */
    .app-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.5rem;
    }
    .app-title {
        font-size: 1.9rem;
        font-weight: 800;
        color: #1A1D26;
        letter-spacing: -0.5px;
        margin: 0;
    }
    .diamond-badge {
        background-color: #FFFFFF;
        padding: 8px 14px;
        border-radius: 50px;
        box-shadow: 0 3px 10px rgba(0,0,0,0.04);
        font-weight: 700;
        font-size: 0.9rem;
        color: #1A1D26;
    }

    /* ホーム画面のメニューカード（01 自動出題 / 02 苦手出題） */
    div.stButton > button {
        width: 100%;
        background-color: #FFFFFF;
        color: #1A1D26;
        border: none;
        border-radius: 20px;
        padding: 1.6rem 1.5rem;
        font-size: 1.25rem !important;
        font-weight: 800 !important;
        text-align: left !important;
        display: flex;
        justify-content: flex-start;
        align-items: center;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.03);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
        margin-bottom: 0.8rem;
        height: auto;
    }
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.06);
        border: none;
        color: #2B5CE6;
    }
    div.stButton > button:active {
        transform: translateY(1px);
    }

    /* 苦手問題数の赤字バッジ表示用バー */
    .weak-status-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background-color: transparent;
        padding: 0 0.5rem;
        margin-top: -0.4rem;
        margin-bottom: 1.2rem;
        font-size: 0.9rem;
        font-weight: 700;
        color: #6B7280;
    }
    .weak-count-red {
        color: #E03131;
        font-weight: 800;
        font-size: 1rem;
    }

    /* フッター統計（今日 ◯回答） */
    .today-stats {
        text-align: center;
        color: #5A6275;
        font-weight: 700;
        font-size: 0.95rem;
        margin-top: 2rem;
    }

    /* --- 問題画面のカードデザイン --- */
    .q-header-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.8rem;
    }
    .q-meta-tag {
        font-size: 0.85rem;
        font-weight: 700;
        color: #2B5CE6;
        background: #E8F0FE;
        padding: 5px 12px;
        border-radius: 20px;
    }
    .q-rate-tag {
        font-size: 0.85rem;
        font-weight: 700;
        color: #4B5563;
        background: #FFFFFF;
        padding: 5px 12px;
        border-radius: 20px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.04);
    }
    .question-card {
        background-color: #FFFFFF;
        padding: 1.6rem;
        border-radius: 22px;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.04);
        font-size: 1.1rem;
        line-height: 1.75;
        color: #1A1D26;
        margin-bottom: 1.5rem;
        font-weight: 500;
    }

    /* --- スマホでも絶対に横並びになる3つの回答ボタン（◯・？・×） --- */
    div[data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 12px !important;
    }
    div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
        flex: 1 1 33% !important;
        min-width: 0 !important;
    }
    div[data-testid="stHorizontalBlock"] button {
        justify-content: center !important;
        text-align: center !important;
        height: 4.2rem !important;
        border-radius: 18px !important;
        font-size: 1.7rem !important;
        font-weight: 900 !important;
        padding: 0 !important;
    }

    /* 左：正しいボタン（青背景に白丸） */
    div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(1) button {
        background-color: #2563EB !important;
        color: #FFFFFF !important;
        box-shadow: 0 5px 15px rgba(37, 99, 235, 0.25) !important;
    }
    /* 中央：わからないボタン（白背景に黒の？） */
    div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(2) button {
        background-color: #FFFFFF !important;
        color: #111827 !important;
        border: 2px solid #E5E7EB !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04) !important;
    }
    /* 右：誤りボタン（赤背景に白の×） */
    div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(3) button {
        background-color: #DC2626 !important;
        color: #FFFFFF !important;
        box-shadow: 0 5px 15px rgba(220, 38, 38, 0.25) !important;
    }

    /* 解説カード */
    .explanation-card {
        background-color: #FFFFFF;
        padding: 1.4rem;
        border-radius: 18px;
        border-left: 6px solid #2563EB;
        box-shadow: 0 4px 15px rgba(0,0,0,0.03);
        font-size: 0.98rem;
        line-height: 1.65;
        color: #374151;
        margin-top: 0.8rem;
        margin-bottom: 1.2rem;
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

# 科目でフィルタリングした問題リストを取得
def get_filtered_df():
    if st.session_state.selected_subject == "すべての科目":
        return df_all
    return df_all[df_all["科目"] == st.session_state.selected_subject].reset_index(drop=True)

# 苦手問題リスト（間違えた回数が多い順）を取得
def get_weak_qids(target_df):
    q_stats = st.session_state.stats.get("questions", {})
    valid_qids = set(target_df["qid"].tolist())
    weak_items = []
    for qid, st_data in q_stats.items():
        if qid in valid_qids and st_data.get("is_weak", False):
            weak_items.append((qid, st_data.get("wrong", 0)))
    # 間違えた回数（wrong）が多い順に並び替え（同数の場合はランダム性を少し加える）
    random.shuffle(weak_items)
    weak_items.sort(key=lambda x: x[1], reverse=True)
    return [item[0] for item in weak_items]

# 次の問題をセットする関数
def pick_next_question(mode):
    target_df = get_filtered_df()
    if len(target_df) == 0:
        st.session_state.current_qid = None
        return
    if mode == "auto":
        st.session_state.current_qid = random.choice(target_df["qid"].tolist())
    elif mode == "weak":
        weak_qids = get_weak_qids(target_df)
        if len(weak_qids) == 0:
            st.session_state.current_qid = None
        else:
            # 最も間違えている上位グループから優先的に出題（同じ問題ばかり連続しないよう直前と別にする工夫）
            if len(weak_qids) > 1 and weak_qids[0] == st.session_state.current_qid:
                st.session_state.current_qid = weak_qids[1]
            else:
                st.session_state.current_qid = weak_qids[0]

# 回答を記録する関数
def record_answer(qid, choice, correct_ans):
    q_stats = st.session_state.stats.setdefault("questions", {})
    item = q_stats.setdefault(qid, {
        "correct": 0,
        "wrong": 0,
        "streak": 0,
        "is_weak": False
    })

    # 「？」（わからない）は不正解として扱う
    is_correct = (choice == correct_ans)

    if is_correct:
        item["correct"] += 1
        item["streak"] += 1
        # 過去間違えた問題のうち、2回連続で正解したものは苦手リストから削除
        if item["is_weak"] and item["streak"] >= 2:
            item["is_weak"] = False
    else:
        item["wrong"] += 1
        item["streak"] = 0
        item["is_weak"] = True  # 間違えたら苦手リストに登録

    # 今日の回答数をカウント
    today_str = datetime.now().strftime("%Y-%m-%d")
    daily = st.session_state.stats.setdefault("daily", {})
    daily[today_str] = daily.get(today_str, 0) + 1

    save_stats(st.session_state.stats)

# ==========================================
# 🏠 5. ホーム画面の表示
# ==========================================
if st.session_state.page == "home":
    today_str = datetime.now().strftime("%Y-%m-%d")
    today_count = st.session_state.stats.get("daily", {}).get(today_str, 0)

    # 上部ヘッダー（Memora X風）
    st.markdown(f"""
    <div class="app-header">
        <h1 class="app-title">Benrishi X</h1>
        <div class="diamond-badge">💎 {today_count}</div>
    </div>
    """, unsafe_allow_html=True)

    # 科目プルダウン（Memora Xの「英単語 ▼」部分）
    subjects = ["すべての科目"] + list(df_all["科目"].unique())
    selected = st.selectbox("科目選択", subjects, index=subjects.index(st.session_state.selected_subject), label_visibility="collapsed")
    if selected != st.session_state.selected_subject:
        st.session_state.selected_subject = selected
        st.rerun()

    target_df = get_filtered_df()
    weak_qids = get_weak_qids(target_df)
    weak_count = len(weak_qids)

    st.write("")

    # 01 自動出題カード
    if st.button("01 自動出題"):
        st.session_state.page = "auto"
        st.session_state.answered = False
        st.session_state.user_choice = None
        pick_next_question("auto")
        st.rerun()

    # 02 苦手出題カード
    if st.button("02 苦手出題"):
        if weak_count == 0:
            st.toast("🎉 現在、苦手問題はありません！「自動出題」で演習を進めましょう。")
        else:
            st.session_state.page = "weak"
            st.session_state.answered = False
            st.session_state.user_choice = None
            pick_next_question("weak")
            st.rerun()

    # 苦手問題数の赤字インジケーター
    st.markdown(f"""
    <div class="weak-status-bar">
        <span>※2回連続正解で苦手リストから自動卒業</span>
        <span class="weak-count-red">苦手残り：{weak_count} 問</span>
    </div>
    """, unsafe_allow_html=True)

    # 下部ステータス（今日 ◯回答 ・ 登録 ◯問）
    st.markdown(f"""
    <div class="today-stats">
        今日 {today_count} 回答 ・ 収録 {len(target_df)} 問
    </div>
    """, unsafe_allow_html=True)

    st.write("")
    st.write("")
    col_r1, col_r2, col_r3 = st.columns([1, 2, 1])
    with col_r2:
        if st.button("🔄 最新のスプレッドシート読込"):
            st.cache_data.clear()
            st.toast("最新の問題データを読み込みました！")
            st.rerun()

# ==========================================
# 📝 6. 出題画面（自動出題 / 苦手出題）
# ==========================================
else:
    target_df = get_filtered_df()
    mode_label = "01 自動出題" if st.session_state.page == "auto" else "02 苦手出題（優先復習）"

    # 苦手出題モードで全問クリアした場合
    if st.session_state.current_qid is None:
        st.balloons()
        st.success("🎉 すべての苦手問題をクリア（2回連続正解）しました！素晴らしいです！")
        if st.button("🏠 ホーム画面へ戻る"):
            st.session_state.page = "home"
            st.rerun()
        st.stop()

    # 現在の問題データを取得
    matched = target_df[target_df["qid"] == st.session_state.current_qid]
    if len(matched) == 0:
        pick_next_question(st.session_state.page)
        st.rerun()
    row = matched.iloc[0]
    qid = row["qid"]

    # 問題ごとの正答率を計算
    q_stat = st.session_state.stats.get("questions", {}).get(qid, {"correct": 0, "wrong": 0, "streak": 0, "is_weak": False})
    total_try = q_stat["correct"] + q_stat["wrong"]
    if total_try > 0:
        acc_rate = int((q_stat["correct"] / total_try) * 100)
        rate_str = f"正答率 {acc_rate}% ({q_stat['correct']}/{total_try})"
    else:
        rate_str = "初挑戦 (正答率 --%)"

    # 苦手モードの場合は間違えた回数も表示
    if st.session_state.page == "weak":
        rate_str += f" ｜ ❌累計 {q_stat['wrong']}回"

    # 上部ナビゲーション＆正答率バッジ
    st.markdown(f"""
    <div class="q-header-bar">
        <span class="q-meta-tag">{mode_label}</span>
        <span class="q-rate-tag">📊 {rate_str}</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"**【{row['科目']}】 {row['年度・問題番号']} （枝 {row['枝番']}）**")

    # 問題文カード
    st.markdown(f"<div class='question-card'>{row['問題文']}</div>", unsafe_allow_html=True)

    # --- 回答ボタン（左から 青◯ / 白？ / 赤× の横並び） ---
    col_o, col_q, col_x = st.columns(3)
    with col_o:
        if st.button("◯", key="btn_o", disabled=st.session_state.answered):
            st.session_state.answered = True
            st.session_state.user_choice = "◯"
            record_answer(qid, "◯", row["正解"])
            st.rerun()
    with col_q:
        if st.button("？", key="btn_q", disabled=st.session_state.answered):
            st.session_state.answered = True
            st.session_state.user_choice = "？"
            record_answer(qid, "？", row["正解"])
            st.rerun()
    with col_x:
        if st.button("×", key="btn_x", disabled=st.session_state.answered):
            st.session_state.answered = True
            st.session_state.user_choice = "×"
            record_answer(qid, "×", row["正解"])
            st.rerun()

    # --- 回答後の正誤判定と解説 ---
    if st.session_state.answered:
        updated_stat = st.session_state.stats["questions"][qid]
        if st.session_state.user_choice == row["正解"]:
            if st.session_state.page == "weak" and not updated_stat["is_weak"]:
                st.success(f"⭕ **大正解！（正解：{row['正解']}）** 🎓 2回連続正解したため、苦手リストから卒業しました！")
            else:
                st.success(f"⭕ **大正解！** （正解：{row['正解']} ｜ 連続正解: {updated_stat['streak']}回）")
        elif st.session_state.user_choice == "？":
            st.warning(f"🤔 **わからない（正解は「{row['正解']}」）** 📌 苦手問題リストに登録しました。")
        else:
            st.error(f"❌ **不正解...（正解は「{row['正解']}」）** 📌 苦手問題リストに登録しました。")

        # 解説カード
        st.markdown(f"""
        <div class="explanation-card">
            <strong>💡 解説</strong><br><br>
            {row['解説']}
        </div>
        """, unsafe_allow_html=True)

        # 次の問題へ進むボタン
        if st.button("➡️ 次の問題へ進む"):
            st.session_state.answered = False
            st.session_state.user_choice = None
            pick_next_question(st.session_state.page)
            st.rerun()

    st.write("")
    if st.button("🏠 ホームに戻る"):
        st.session_state.page = "home"
        st.session_state.answered = False
        st.rerun()
