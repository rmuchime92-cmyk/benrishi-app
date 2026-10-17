import streamlit as st
import pandas as pd
import random
import json
import os
import re
import threading  # ⚡ バックグラウンド通信用（待ち時間ゼロ化）
import requests
from datetime import datetime, timedelta

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
        margin-bottom: 1.0rem;
        font-size: 0.82rem;
        font-weight: 700;
        color: #6B7280;
    }
    .weak-count-red { color: #E03131; font-weight: 800; font-size: 0.95rem; }
    .today-stats { text-align: center; color: #5A6275; font-weight: 700; font-size: 0.85rem; margin: 0.8rem 0; }

    .q-header-bar {
        display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.6rem; gap: 6px;
    }
    .q-meta-tag { font-size: 0.8rem; font-weight: 700; color: #2B5CE6; background: #E8F0FE; padding: 4px 10px; border-radius: 20px; }
    .q-rate-tag { font-size: 0.8rem; font-weight: 700; color: #4B5563; background: #FFFFFF; padding: 4px 10px; border-radius: 20px; box-shadow: 0 2px 6px rgba(0,0,0,0.04); }
    .question-card {
        background-color: #FFFFFF; padding: 1.25rem; border-radius: 20px; box-shadow: 0 6px 20px rgba(0, 0, 0, 0.04);
        font-size: 1.05rem; line-height: 1.7; color: #1A1D26; margin-bottom: 1.2rem; font-weight: 500;
    }

    div[data-testid="stHorizontalBlock"] {
        display: flex !important; flex-direction: row !important; flex-wrap: nowrap !important; width: 100% !important; gap: 10px !important; margin: 0 !important; padding: 0 !important;
    }
    div[data-testid="stHorizontalBlock"] > div[data-testid="column"],
    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
        flex: 1 1 0% !important; width: 33.33% !important; min-width: 0 !important; padding: 0 !important;
    }
    div[data-testid="stHorizontalBlock"] button {
        width: 100% !important; min-width: 100% !important; height: 4.8rem !important; border-radius: 18px !important;
        display: flex !important; justify-content: center !important; align-items: center !important; text-align: center !important; padding: 0 !important; margin: 0 !important;
    }
    div[data-testid="stHorizontalBlock"] button p { font-size: 2rem !important; font-weight: 900 !important; margin: 0 !important; line-height: 1 !important; }

    div[data-testid="stHorizontalBlock"] > div:nth-child(1) button { background-color: #2563EB !important; color: #FFFFFF !important; box-shadow: 0 5px 15px rgba(37, 99, 235, 0.28) !important; }
    div[data-testid="stHorizontalBlock"] > div:nth-child(2) button { background-color: #FFFFFF !important; color: #111827 !important; border: 2px solid #D1D5DB !important; }
    div[data-testid="stHorizontalBlock"] > div:nth-child(3) button { background-color: #DC2626 !important; color: #FFFFFF !important; box-shadow: 0 5px 15px rgba(220, 38, 38, 0.28) !important; }

    .explanation-card {
        background-color: #FFFFFF; padding: 1.2rem; border-radius: 18px; border-left: 6px solid #2563EB;
        box-shadow: 0 4px 15px rgba(0,0,0,0.03); font-size: 0.95rem; line-height: 1.65; color: #374151; margin-top: 0.8rem; margin-bottom: 1.2rem;
    }
</style>
""",
    unsafe_allow_html=True,
)

# --- 3. 条文抽出関数 ＆ スプレッドシート読み込み（⚡1時間キャッシュ＆事前抽出） ---
CSV_URL = "https://docs.google.com/spreadsheets/d/1PzRg1YruyR-7tRcOs289Zob1g9diKQxZFlsEnoxiqb0/export?format=csv"

ARTICLE_PATTERN = re.compile(r"(特|実|意|商|民訴法|民訴|行訴法|青本特|青本実)?(\d+条(?:の\d+)*)")
BASIS_PATTERN = re.compile(r"【根拠：(.*?)】")

def extract_articles_from_text(explanation_text):
    text = str(explanation_text)
    match = BASIS_PATTERN.search(text)
    target = match.group(1) if match else text
    articles = set()
    current_law = "特"
    for law_prefix, art_num in ARTICLE_PATTERN.findall(target):
        if law_prefix in ["特", "青本特"]:
            current_law = "特"
        elif law_prefix in ["実", "青本実"]:
            current_law = "実"
        elif law_prefix in ["意", "商"]:
            current_law = law_prefix
        elif law_prefix in ["民訴法", "民訴"]:
            current_law = "民訴"
        elif law_prefix == "行訴法":
            current_law = "行訴"
        articles.add(f"{current_law}{art_num}")
    return list(articles)

@st.cache_data(ttl=3600)  # ⚡ 60秒→3600秒（1時間）に延長して通信の引っかかりを解消
def load_questions():
    df = pd.read_csv(CSV_URL)
    df = df.dropna(subset=["問題文"]).reset_index(drop=True)
    df["qid"] = (
        df["科目"].astype(str)
        + "_"
        + df["年度・問題番号"].astype(str)
        + "_"
        + df["枝番"].astype(str)
    )
    # ⚡ 読み込み時にあらかじめ条文リストを抽出しておく（毎回の計算をゼロにする）
    df["articles"] = df["解説"].apply(extract_articles_from_text)
    return df

try:
    df_all = load_questions()
except Exception:
    st.error("スプレッドシートの読み込みに失敗しました。共有設定を確認してください。")
    st.stop()

# --- 4. クラウド同期（⚡非同期バックグラウンド保存 ＆ メモリキャッシュ） ---
GAS_WEB_APP_URL = st.secrets.get("GAS_URL", "")
DAILY_GOAL = 10

@st.cache_resource
def get_server_stats_cache():
    """サーバーが起動している間、全セッションで共有できる高速メモリキャッシュ"""
    return {"data": None}

server_cache = get_server_stats_cache()

def load_stats_from_cloud(force_fetch=False):
    """初回または明示的な更新時のみGASから取得し、普段はメモリから0秒で返す"""
    if not force_fetch and server_cache["data"] is not None:
        return server_cache["data"]

    if not GAS_WEB_APP_URL:
        return {"questions": {}, "daily": {}}
    try:
        response = requests.get(GAS_WEB_APP_URL, timeout=5)
        if response.status_code == 200:
            data = response.json()
            server_cache["data"] = data
            return data
    except Exception:
        pass
    return server_cache["data"] or {"questions": {}, "daily": {}}

def _post_to_gas_worker(url, payload_str):
    """裏側（別スレッド）で実行される通信処理"""
    try:
        requests.post(
            url,
            data=payload_str.encode("utf-8"),
            headers={"Content-Type": "application/json"},
            timeout=10,
        )
    except Exception:
        pass

def save_stats_to_cloud_async(stats_data):
    """⚡ 画面を一切止めずに裏側でスプレッドシートへ保存する"""
    server_cache["data"] = stats_data
    if not GAS_WEB_APP_URL:
        return
    payload_str = json.dumps(stats_data, ensure_ascii=False)
    thread = threading.Thread(target=_post_to_gas_worker, args=(GAS_WEB_APP_URL, payload_str))
    thread.daemon = True
    thread.start()

if "stats" not in st.session_state:
    st.session_state.stats = load_stats_from_cloud()
if "page" not in st.session_state:
    st.session_state.page = "home"
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

# --- 5. 集計ロジック ---
def calculate_streak(daily_dict):
    today = datetime.now().date()
    streak = 0
    check_date = today
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
    daily_sum = sum(stats_data.get("daily", {}).values())
    q_sum = sum(
        q.get("correct", 0) + q.get("wrong", 0)
        for q in stats_data.get("questions", {}).values()
    )
    return max(daily_sum, q_sum)

def compute_article_heatmap_data(target_df, q_stats):
    art_stats = {}
    # ⚡ 事前抽出した「articles」列をそのまま使うので一瞬で完了
    q_map = target_df.set_index("qid")["articles"].to_dict()
    for qid, st_data in q_stats.items():
        arts = q_map.get(qid)
        if not arts:
            continue
        c = st_data.get("correct", 0)
        w = st_data.get("wrong", 0)
        total = c + w
        if total == 0:
            continue
        for art in arts:
            if art not in art_stats:
                art_stats[art] = {"correct": 0, "total": 0}
            art_stats[art]["correct"] += c
            art_stats[art]["total"] += total
    return art_stats

def sort_article_key(art_name):
    law_order = {"特": 0, "実": 1, "意": 2, "商": 3, "民訴": 4, "行訴": 5}
    prefix = re.match(r"^[^\d]+", art_name)
    p_str = prefix.group(0) if prefix else ""
    order = law_order.get(p_str, 99)
    nums = [int(n) for n in re.findall(r"\d+", art_name)]
    return (order, nums)

def get_filtered_df():
    if st.session_state.selected_subject == "すべての科目":
        return df_all
    return df_all[df_all["科目"] == st.session_state.selected_subject].reset_index(drop=True)

def get_weak_qids(target_df):
    q_stats = st.session_state.stats.get("questions", {})
    valid_qids = set(target_df["qid"].tolist())
    weak_items = []
    for qid, st_data in q_stats.items():
        if qid in valid_qids and st_data.get("is_weak", False):
            weak_items.append((qid, st_data.get("wrong", 0)))
    random.shuffle(weak_items)
    weak_items.sort(key=lambda x: x[1], reverse=True)
    return [item[0] for item in weak_items]

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
            if len(weak_qids) > 1 and weak_qids[0] == st.session_state.current_qid:
                st.session_state.current_qid = weak_qids[1]
            else:
                st.session_state.current_qid = weak_qids[0]

def record_answer(qid, choice, correct_ans):
    q_stats = st.session_state.stats.setdefault("questions", {})
    item = q_stats.setdefault(
        qid, {"correct": 0, "wrong": 0, "streak": 0, "is_weak": False}
    )

    is_correct = choice == correct_ans
    if is_correct:
        item["correct"] += 1
        item["streak"] += 1
        if item["is_weak"] and item["streak"] >= 2:
            item["is_weak"] = False
    else:
        item["wrong"] += 1
        item["streak"] = 0
        item["is_weak"] = True

    today_str = datetime.now().strftime("%Y-%m-%d")
    daily = st.session_state.stats.setdefault("daily", {})
    prev_count = daily.get(today_str, 0)
    daily[today_str] = prev_count + 1

    if prev_count < DAILY_GOAL and daily[today_str] == DAILY_GOAL:
        st.session_state.just_hit_goal = True

    # ⚡ 非同期でクラウドへ保存（待ち時間ゼロ！）
    save_stats_to_cloud_async(st.session_state.stats)

# ==========================================
# 🏠 6. ホーム画面の表示
# ==========================================
if st.session_state.page == "home":
    today_str = datetime.now().strftime("%Y-%m-%d")
    daily_dict = st.session_state.stats.get("daily", {})
    today_count = daily_dict.get(today_str, 0)
    streak_days = calculate_streak(daily_dict)
    total_answers = calculate_total_answers(st.session_state.stats)

    st.markdown(
        f"""
    <div class="app-header">
        <h1 class="app-title">Benrishi X</h1>
        <div class="badge-group">
            <div class="stat-pill" title="連続学習日数">🔥 {streak_days}日</div>
            <div class="stat-pill" title="累計回答数">📚 累計 {total_answers}</div>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    progress_pct = min(int((today_count / DAILY_GOAL) * 100), 100)
    if today_count >= DAILY_GOAL:
        sub_html = f'<span class="goal-sub-done">🎉 目標達成！ ({today_count} / {DAILY_GOAL}問)</span>'
        fill_class = "progress-fill-done"
    else:
        rem = DAILY_GOAL - today_count
        sub_html = f'<span class="goal-sub">{today_count} / {DAILY_GOAL}問（あと{rem}問）</span>'
        fill_class = "progress-fill"

    st.markdown(
        f"""
    <div class="goal-card">
        <div class="goal-header">
            <span>🎯 今日のノルマ</span>
            {sub_html}
        </div>
        <div class="progress-track">
            <div class="{fill_class}" style="width: {progress_pct}%;"></div>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    subjects = ["すべての科目"] + list(df_all["科目"].unique())
    selected = st.selectbox(
        "科目選択",
        subjects,
        index=subjects.index(st.session_state.selected_subject),
        label_visibility="collapsed",
    )
    if selected != st.session_state.selected_subject:
        st.session_state.selected_subject = selected
        st.rerun()

    target_df = get_filtered_df()
    weak_qids = get_weak_qids(target_df)
    weak_count = len(weak_qids)

    st.write("")

    if st.button("01 自動出題", use_container_width=True):
        st.session_state.page = "auto"
        st.session_state.answered = False
        st.session_state.user_choice = None
        pick_next_question("auto")
        st.rerun()

    if st.button("02 苦手出題", use_container_width=True):
        if weak_count == 0:
            st.toast("🎉 現在、苦手問題はありません！「自動出題」で演習を進めましょう。")
        else:
            st.session_state.page = "weak"
            st.session_state.answered = False
            st.session_state.user_choice = None
            pick_next_question("weak")
            st.rerun()

    st.markdown(
        f"""
    <div class="weak-status-bar">
        <span>※2回連続正解で苦手から自動卒業</span>
        <span class="weak-count-red">苦手残り：{weak_count} 問</span>
    </div>
    """,
        unsafe_allow_html=True,
    )

    art_stats = compute_article_heatmap_data(
        target_df, st.session_state.stats.get("questions", {})
    )
    if art_stats:
        sorted_arts = sorted(art_stats.keys(), key=sort_article_key)
        tiles_html = ""
        for art in sorted_arts:
            c = art_stats[art]["correct"]
            t = art_stats[art]["total"]
            rate = int((c / t) * 100) if t > 0 else 0
            color_cls = (
                "hm-green" if rate >= 80 else ("hm-yellow" if rate >= 50 else "hm-red")
            )
            tiles_html += (
                f'<div class="hm-tile {color_cls}" title="正解 {c}/{t}">'
                f'{art}<span class="hm-sub">{rate}% ({c}/{t})</span>'
                f"</div>"
            )

        st.markdown(
            f"""
        <div class="heatmap-card">
            <div class="heatmap-title">
                <span>🗺️ 条文マスターヒートマップ ({len(sorted_arts)}条文)</span>
                <span class="heatmap-legend">🟩80%~ 🟨50%~ 🟥~49%</span>
            </div>
            <div class="heatmap-grid">
                {tiles_html}
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    st.markdown(
        f"""
    <div class="today-stats">
        ⚡ 高速クラウド同期中 ・ 今日 {today_count} 回答 ・ 累計 {total_answers} 回答
    </div>
    """,
        unsafe_allow_html=True,
    )

    if st.button("🔄 最新のスプレッドシート＆履歴を再読込", use_container_width=True):
        st.cache_data.clear()
        st.session_state.stats = load_stats_from_cloud(force_fetch=True)
        st.toast("クラウドから最新データを同期しました！")
        st.rerun()

# ==========================================
# 📝 7. 出題画面
# ==========================================
else:
    target_df = get_filtered_df()
    mode_label = "01 自動出題" if st.session_state.page == "auto" else "02 苦手出題"

    if st.session_state.current_qid is None:
        st.balloons()
        st.success("🎉 すべての苦手問題をクリア（2回連続正解）しました！素晴らしいです！")
        if st.button("🏠 ホーム画面へ戻る", use_container_width=True):
            st.session_state.page = "home"
            st.rerun()
        st.stop()

    matched = target_df[target_df["qid"] == st.session_state.current_qid]
    if len(matched) == 0:
        pick_next_question(st.session_state.page)
        st.rerun()
    row = matched.iloc[0]
    qid = row["qid"]

    today_str = datetime.now().strftime("%Y-%m-%d")
    today_count = st.session_state.stats.get("daily", {}).get(today_str, 0)

    q_stat = st.session_state.stats.get("questions", {}).get(
        qid, {"correct": 0, "wrong": 0, "streak": 0, "is_weak": False}
    )
    total_try = q_stat["correct"] + q_stat["wrong"]
    rate_str = (
        f"正答率 {int((q_stat['correct'] / total_try) * 100)}% ({q_stat['correct']}/{total_try})"
        if total_try > 0
        else "初挑戦 (--%)"
    )
    if st.session_state.page == "weak":
        rate_str += f" ｜ ❌{q_stat['wrong']}回"

    st.markdown(
        f"""
    <div class="q-header-bar">
        <span class="q-meta-tag">{mode_label} （今日 {today_count}/{DAILY_GOAL}問）</span>
        <span class="q-rate-tag">📊 {rate_str}</span>
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown(f"**【{row['科目']}】 {row['年度・問題番号']} （枝 {row['枝番']}）**")
    st.markdown(f"<div class='question-card'>{row['問題文']}</div>", unsafe_allow_html=True)

    col_o, col_q, col_x = st.columns(3)
    with col_o:
        if st.button("◯", key="btn_o", disabled=st.session_state.answered, use_container_width=True):
            st.session_state.answered = True
            st.session_state.user_choice = "◯"
            record_answer(qid, "◯", row["正解"])
            st.rerun()
    with col_q:
        if st.button("？", key="btn_q", disabled=st.session_state.answered, use_container_width=True):
            st.session_state.answered = True
            st.session_state.user_choice = "？"
            record_answer(qid, "？", row["正解"])
            st.rerun()
    with col_x:
        if st.button("×", key="btn_x", disabled=st.session_state.answered, use_container_width=True):
            st.session_state.answered = True
            st.session_state.user_choice = "×"
            record_answer(qid, "×", row["正解"])
            st.rerun()

    if st.session_state.answered:
        if st.session_state.just_hit_goal:
            st.balloons()
            st.toast("🎉 今日の目標（10問）を達成しました！ナイスファイトです！")
            st.session_state.just_hit_goal = False

        updated_stat = st.session_state.stats["questions"][qid]
        if st.session_state.user_choice == row["正解"]:
            if st.session_state.page == "weak" and not updated_stat["is_weak"]:
                st.success(f"⭕ **大正解！（正解：{row['正解']}）** 🎓 2回連続正解で苦手リストから卒業しました！")
            else:
                st.success(f"⭕ **大正解！** （正解：{row['正解']} ｜ 連続正解: {updated_stat['streak']}回）")
        elif st.session_state.user_choice == "？":
            st.warning(f"🤔 **わからない（正解は「{row['正解']}」）** 📌 苦手問題リストに登録しました。")
        else:
            st.error(f"❌ **不正解...（正解は「{row['正解']}」）** 📌 苦手問題リストに登録しました。")

        st.markdown(
            f"""
        <div class="explanation-card">
            <strong>💡 解説</strong><br><br>
            {row['解説']}
        </div>
        """,
            unsafe_allow_html=True,
        )

        if st.button("➡️ 次の問題へ進む", use_container_width=True):
            st.session_state.answered = False
            st.session_state.user_choice = None
            pick_next_question(st.session_state.page)
            st.rerun()

    st.write("")
    if st.button("🏠 ホームに戻る", use_container_width=True):
        st.session_state.page = "home"
        st.session_state.answered = False
        st.rerun()
