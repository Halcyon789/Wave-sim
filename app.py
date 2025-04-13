
import streamlit as st
import json
import os
import time
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt

st.set_page_config(page_title="ψ(t) Chat", layout="centered")

# 사용자 고정
query_params = st.query_params
username = query_params.get("user", ["guest"])[0]

# 메시지 파일
DATA_FILE = "message_log.json"
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump([], f)

# 메시지 로딩
with open(DATA_FILE, "r") as f:
    messages = json.load(f)

# 채팅 UI 상단
st.title("ψ(t) Emotional Wave Chat")
st.markdown(f"**You are:** :blue[{username}]")

# 채팅 출력
st.subheader("Live Messages")
chat_area = st.container()
for msg in messages[-30:]:
    align = "flex-start" if msg["user"] != username else "flex-end"
    bg = "#f0f0f0" if align == "flex-start" else "#d1e7dd"
    chat_area.markdown(f"""
    <div style='display: flex; justify-content: {align};'>
        <div style='background-color: {bg}; padding: 10px 14px; border-radius: 10px;
                    margin: 4px; max-width: 80%;'>
            <b>{msg['user']}</b><br>{msg['message']}<br>
            <small>ψ = {msg['psi']}, {msg['time']}</small>
        </div>
    </div>
    """, unsafe_allow_html=True)

# 입력창 아래 배치
st.markdown("---")
st.subheader("Send a Message")
with st.form(key="send_form", clear_on_submit=True):
    new_msg = st.text_input("Type your message:")
    send = st.form_submit_button("Send")
    if send and new_msg.strip():
        psi = round(np.clip(np.random.normal(0.5, 0.2), 0, 1), 2)
        messages.append({
            "user": username,
            "message": new_msg.strip(),
            "psi": psi,
            "time": datetime.now().strftime('%H:%M:%S')
        })
        with open(DATA_FILE, "w") as f:
            json.dump(messages, f, indent=2)
        st.experimental_rerun()

# 공명도 계산
user_data = [m for m in messages if m["user"] == username]
other_users = set(m["user"] for m in messages if m["user"] != username)

if user_data and other_users:
    st.subheader("Resonance")
    y = [m["psi"] for m in user_data]
    for other in other_users:
        other_data = [m["psi"] for m in messages if m["user"] == other]
        min_len = min(len(y), len(other_data))
        if min_len > 1:
            sim = np.corrcoef(y[-min_len:], other_data[-min_len:])[0, 1]
            st.write(f"Resonance with **{other}**: :green[{sim:.2f}]")

# 파동 시각화
st.subheader("Your ψ(t) Wave")
if user_data:
    fig, ax = plt.subplots()
    ax.plot([m["psi"] for m in user_data], marker="o", label=f"{username}")
    ax.set_ylim(0, 1)
    ax.set_xlabel("Message Index")
    ax.set_ylabel("ψ(t)")
    ax.set_title(f"{username}'s Emotional Wave")
    ax.legend()
    st.pyplot(fig)
