
import streamlit as st
import json
import os
import time
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from difflib import SequenceMatcher

st.set_page_config(page_title="ψ(t) Emotional Wave Chat", layout="centered")

DATA_FILE = "message_log.json"

# 사용자 구분
query_params = st.query_params
username = query_params.get("user", ["guest"])[0]

# 세션 초기화
if "messages" not in st.session_state:
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            st.session_state.messages = json.load(f)
    else:
        st.session_state.messages = []

if "input_text" not in st.session_state:
    st.session_state.input_text = ""

st.title("ψ(t) Emotional Wave Chat")
st.markdown(f"**Current User:** `{username}`")

# 메시지 입력
message = st.text_input("Enter your message", value=st.session_state.input_text, key="input_box")

if st.button("Send"):
    psi = round(np.clip(np.random.normal(0.5, 0.2), 0, 1), 2)
    timestamp = datetime.now().isoformat()
    new_entry = {
        "user": username,
        "message": message,
        "psi": psi,
        "timestamp": timestamp
    }
    st.session_state.messages.append(new_entry)

    # Save to file
    with open(DATA_FILE, "w") as f:
        json.dump(st.session_state.messages, f, indent=2)

    # Clear text after sending
    st.session_state.input_text = ""
    st.rerun()

# 메시지 박스
st.markdown("### Chat")
chat_box = st.container()
recent_msgs = [msg for msg in st.session_state.messages if msg["user"] == username][-10:]

for msg in st.session_state.messages[-20:]:
    user_color = "lightgreen" if msg["user"] == username else "lightblue"
    chat_box.markdown(
        f"<div style='background-color:{user_color}; padding:6px; margin:4px; border-radius:6px;'>"
        f"<b>{msg['user']}</b>: {msg['message']}<br><small>ψ(t): {msg['psi']}</small></div>",
        unsafe_allow_html=True
    )

# ψ(t) 시각화
st.markdown("### Your ψ(t) Wave")
user_data = [m for m in st.session_state.messages if m["user"] == username]
other_users = set(m["user"] for m in st.session_state.messages if m["user"] != username)

plt.figure(figsize=(6, 3))
x = list(range(len(user_data)))
y = [m["psi"] for m in user_data]
plt.plot(x, y, marker="o", label=f"{username}")
plt.xlabel("Message Index")
plt.ylabel("ψ(t)")
plt.legend()
plt.tight_layout()
st.pyplot(plt)

# 공명도 계산
if other_users:
    st.markdown("### Resonance with Other Users")
    for other in other_users:
        other_data = [m["psi"] for m in st.session_state.messages if m["user"] == other]
        min_len = min(len(y), len(other_data))
        if min_len > 1:
            similarity = np.corrcoef(y[-min_len:], other_data[-min_len:])[0, 1]
            st.write(f"Resonance with **{other}**: {similarity:.2f}")
        else:
            st.write(f"Not enough data to compare with **{other}**")
