import streamlit as st
import time
from google import genai

# ==========================================
# 0. APIキーの設定
# ==========================================
API_KEY = st.secrets["GEMINI_API_KEY"]

# ==========================================
# 1. 問題データの準備
# ==========================================
questions = [
    {
        "id": 1,
        "subject": "特許法",
        "question": "特許出願の分割（特許法第44条）は、特許査定の謄本送達後においても、一定の期間内であれば行うことができる。正しいか誤りか。",
        "choices": ["正しい", "誤り"],
        "answer": "正しい",
        "explanation": "特許法第44条第1項第2号の規定により、特許査定の謄本送達があった日から30日以内であれば分割出願が可能です。"
    },
    {
        "id": 2,
        "subject": "実用新案法",
        "question": "実用新案技術評価書の請求は、出願人以外の何人も行うことができない。正しいか誤りか。",
        "choices": ["正しい", "誤り"],
        "answer": "誤り",
        "explanation": "実用新案法第12条第1項の規定により、何人も、実用新案権の設定の登録があった後は、実用新案技術評価書を請求することができます。"
    }
]

# ==========================================
# 2. アプリの状態（State）を管理する
# ==========================================
if "current_q_index" not in st.session_state:
    st.session_state.current_q_index = 0
if "show_explanation" not in st.session_state:
    st.session_state.show_explanation = False
if "user_answer" not in st.session_state:
    st.session_state.user_answer = None
if "ai_response" not in st.session_state:
    st.session_state.ai_response = None

current_q = questions[st.session_state.current_q_index]

# ==========================================
# 3. 画面の描画（UI）
# ==========================================
st.title("弁理士試験 短答式対策アプリ")
st.caption(f"全 {len(questions)} 問中 / {st.session_state.current_q_index + 1} 問目 （科目：{current_q['subject']}）")

st.subheader("問題")
st.write(current_q["question"])

# ==========================================
# 4. 回答フォームと解説
# ==========================================
if not st.session_state.show_explanation:
    selected_option = st.radio("選択肢を選んでください：", current_q["choices"])
    if st.button("回答する"):
        st.session_state.user_answer = selected_option
        st.session_state.show_explanation = True
        st.rerun()

else:
    st.write(f"あなたの回答: **{st.session_state.user_answer}**")
    if st.session_state.user_answer == current_q["answer"]:
        st.success("正解です！")
    else:
        st.error(f"不正解です。正解は「{current_q['answer']}」です。")
    
    st.info(f"【解説】\n{current_q['explanation']}")
    
    # ----------------------------------------
    # 5. AI講師への深掘り質問エリア（自動リトライ機能付き）
    # ----------------------------------------
    st.divider()
    st.subheader("🤖 AI講師に深掘り質問")
    
    user_question = st.text_input("解説で分からない点や、関連する条文（拒絶査定の場合は？など）について質問してください：")
    
    if st.button("AIに質問する"):
        if user_question:
            with st.spinner("AI講師が回答を作成しています..."):
                client = genai.Client(api_key=API_KEY)
                prompt = f"""
                あなたは厳密で分かりやすい弁理士試験の専任講師です。
                以下の【問題】と【解説】に関する生徒からの【質問】に答えてください。
                必要に応じて関連する条文の趣旨や、試験での引っ掛けポイントなども解説してください。

                【問題】{current_q['question']}
                【正解】{current_q['answer']}
                【基本解説】{current_q['explanation']}

                【生徒の質問】{user_question}
                """
                
                # 最大3回まで自動で再試行する仕組み
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        response = client.models.generate_content(
                            model='gemini-3.8-flash',
                            contents=prompt
                        )
                        st.session_state.ai_response = response.text
                        break # 成功したらループを抜ける
                    except Exception as e:
                        if "503" in str(e) and attempt < max_retries - 1:
                            # 503エラー（混雑）の場合は、2秒待ってからもう一度試す
                            time.sleep(2)
                            continue
                        else:
                            # 3回試してもダメだった場合や別のエラーの場合は画面に表示
                            st.error(f"サーバーが混み合っているため、少し時間をおいて再度お試しください。（詳細: {e}）")
                            break

    if st.session_state.ai_response:
        st.success(st.session_state.ai_response)

    # ----------------------------------------
    # 6. 次の問題へ進む処理
    # ----------------------------------------
    st.divider()
    if st.session_state.current_q_index < len(questions) - 1:
        if st.button("次の問題へ"):
            st.session_state.current_q_index += 1
            st.session_state.show_explanation = False
            st.session_state.user_answer = None
            st.session_state.ai_response = None
            st.rerun()
    else:
        st.write("すべての問題が終了しました！お疲れ様でした。")
        if st.button("最初からやり直す"):
            st.session_state.current_q_index = 0
            st.session_state.show_explanation = False
            st.session_state.user_answer = None
            st.session_state.ai_response = None
            st.rerun()