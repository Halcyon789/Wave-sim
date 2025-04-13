
import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# 페이지 설정은 반드시 최상단에 위치
st.set_page_config(page_title="ψ(t) Emotional Chat", layout="wide")

# 쿼리 파라미터로 사용자 식별
params = st.query_params
user = params.get("user", ["guest"])[0]

# 파일 경로
LOG_PATH = "message_log.json"

# 메시지 불러오기
def load_messages():
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH, "r") as f:
            return json.load(f)
    return []

# 메시지 저장
def save_messages(messages):
    with open(LOG_PATH, "w") as f:
        json.dump(messages, f, indent=2)

# 감정 파동 함수 예시
def compute_psi(text: str) -> float:
    return round(min(1.0, max(0.0, len(text.strip()) / 50)), 2)

# 초기화
if "messages" not in st.session_state:
    st.session_state.messages = load_messages()

st.title("ψ(t) Emotional Wave Chat")
st.markdown(f"**You are:** `{user}`")

# 채팅 입력 박스 하단에 배치
for msg in st.session_state.messages:
    st.markdown(f"**{msg['user']}**: {msg['text']} | ψ(t): `{msg['psi']}`")

st.markdown("---")

message = st.text_input("Enter your message", key="input_msg")
if st.button("Send", type="primary") and message.strip():
    psi = compute_psi(message)
    new_msg = {
        "user": user,
        "text": message.strip(),
        "psi": psi,
        "timestamp": datetime.now().isoformat()
    }
    st.session_state.messages.append(new_msg)
    save_messages(st.session_state.messages)
    st.rerun()

# 그래프 표시
df = pd.DataFrame([m for m in st.session_state.messages if m["user"] == user])
if not df.empty:
    st.line_chart(df["psi"])
