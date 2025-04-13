
import streamlit as st
import json
import os
from datetime import datetime
import matplotlib.pyplot as plt

# 페이지 설정은 가장 첫 줄에서 수행
st.set_page_config(page_title="Wave Sim", layout="centered")

# 쿼리 파라미터로 사용자 ID 고정
query_params = st.query_params
username = query_params.get("user", ["guest"])[0]

# 데이터 파일 경로
DATA_PATH = "message_log.json"

# 메시지 불러오기
def load_messages():
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, "r") as f:
            return json.load(f)
    return []

# 메시지 저장
def save_messages(messages):
    with open(DATA_PATH, "w") as f:
        json.dump(messages, f, indent=2)

# 파동 함수 (감정 강도 임의)
def compute_psi(text):
    return round(len(text.strip()) % 10 / 10, 2)

# 메시지 인터페이스
st.title("ψ(t) Emotional Wave Chat")
st.markdown(f"**Current User:** `{username}`")

new_msg = st.text_input("Enter your message")
if st.button("Send") and new_msg:
    messages = load_messages()
    messages.append({
        "user": username,
        "text": new_msg,
        "psi": compute_psi(new_msg),
        "timestamp": datetime.now().isoformat()
    })
    save_messages(messages)
    st.rerun()

# 메시지 출력
messages = load_messages()
for msg in reversed(messages[-20:]):
    st.markdown(f"**{msg['user']}**: {msg['text']}  |  ψ(t): `{msg['psi']}`")

# 시각화
if messages:
    user_msgs = [m for m in messages if m['user'] == username]
    if user_msgs:
        st.markdown("### Your ψ(t) Wave")
        plt.figure(figsize=(8, 3))
        plt.plot([m["psi"] for m in user_msgs], marker="o", label=f"{username}")
        plt.ylim(0, 1)
        plt.xlabel("Message Index")
        plt.ylabel("ψ(t)")
        plt.legend()
        st.pyplot(plt)
