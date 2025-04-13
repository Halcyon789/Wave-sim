
import streamlit as st
import json
import os
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

st.set_page_config(page_title="ψ(t) Chat", layout="centered")

# 사용자 설정
query_params = st.experimental_get_query_params()
username = query_params.get("user", ["guest"])[0]

# 메시지 저장 파일
DATA_FILE = "message_log.json"
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump([], f)

with open(DATA_FILE, "r") as f:
    messages = json.load(f)

# 헤더
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

# 입력창
st.markdown("---")
st.subheader("Send a Message")
with st.form(key="send_form", clear_on_submit=True):
    new_msg = st.text_input("Type your message here")
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

# 공명도
user_data = [m for m in messages if m["user"] == username]
other_users = set(m["user"] for m in messages if m["user"] != username)

if user_data and other_users:
    st.subheader("Resonance with Other Users")
    y = [m["psi"] for m in user_data]
    for other in other_users:
        other_data = [m["psi"] for m in messages if m["user"] == other]
        min_len = min(len(y), len(other_data))
        if min_len > 1:
            sim = np.corrcoef(y[-min_len:], other_data[-min_len:])[0, 1]
            st.write(f"Resonance with **{other}**: :green[{sim:.2f}]")

# ψ(t) 시각화
st.subheader("Your ψ(t) Wave")
if user_data:
    y_vals = [m["psi"] for m in user_data]
    x_vals = list(range(len(y_vals)))
    fig = plt.figure()
    plt.plot(x_vals, y_vals, marker="o", label=f"{username}")
    plt.ylim(0, 1)
    plt.xlabel("Message Index")
    plt.ylabel("ψ(t)")
    plt.title(f"{username}'s Emotional Wave")
    plt.legend()
    st.pyplot(fig)
