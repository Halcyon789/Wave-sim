
import streamlit as st
import json
import os
import uuid
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="ψ(t) Wave Chat", layout="centered")

# 쿼리 파라미터에서 유저명 받아오기
query_params = st.query_params
username = query_params.get("user", ["guest"])[0]

# 메시지 로그 파일
LOG_FILE = "message_log.json"
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w") as f:
        json.dump([], f)

# 메시지 불러오기
with open(LOG_FILE, "r") as f:
    message_log = json.load(f)

# 메시지 입력
st.title("ψ(t) Emotional Wave Chat")
st.markdown(f"**Current User:** :green[{username}]")

message = st.text_input("Enter your message")
if st.button("Send") and message.strip():
    psi_value = round(len(message.strip()) / 50, 2)
    new_message = {
        "user": username,
        "text": message.strip(),
        "psi": psi_value
    }
    message_log.append(new_message)
    with open(LOG_FILE, "w") as f:
        json.dump(message_log, f, indent=2)
    st.success(f"{username}: {message} | ψ(t): {psi_value}")

# 채팅 내역 출력
st.markdown("### Message Log")
for msg in message_log[-10:]:
    st.markdown(f"**{msg['user']}**: {msg['text']} | ψ(t): :blue[{msg['psi']}]")

# 그래프 출력
df = pd.DataFrame(message_log)
if not df.empty:
    fig, ax = plt.subplots()
    for user in df["user"].unique():
        user_df = df[df["user"] == user]
        ax.plot(user_df.index, user_df["psi"], marker='o', label=user)
    ax.set_title("ψ(t) Wave")
    ax.set_xlabel("Message Index")
    ax.set_ylabel("ψ(t)")
    ax.legend()
    st.pyplot(fig)
