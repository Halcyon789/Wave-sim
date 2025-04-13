# DataFrame 변환 전에 timestamp 필터 추가
data = [d for d in data if "timestamp" in d and d["timestamp"] != ""]

# 이후에 df = pd.DataFrame(data) 수행
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
import requests
import datetime

st.set_page_config(layout="wide")
st.title("ψ(t) Emotional-Cognitive Wave Visualization + Input")

# Google Drive에서 JSON 불러오기
drive_url = "https://drive.google.com/uc?id=1-DZnniFffJJucJkw6Wx4TSmEZpjiahiz"

try:
    res = requests.get(drive_url)
    data = json.loads(res.content)
except:
    data = []

# ψ(t) 계산 함수
def compute_psi(text):
    emotional_keywords = ["love", "miss", "hurt", "hate", "happy", "sad", "alone", "scared", "beautiful", "why", "what"]
    E = sum(word in text.lower() for word in emotional_keywords)
    L = min(len(text) / 100, 1.0)
    S = 0.7 if "?" in text else 0.3
    psi = round(0.5 * E / len(emotional_keywords) + 0.2 * L + 0.3 * S, 2)
    return psi

# 사용자 입력
st.subheader("Write a new message to update ψ(t)")
sender = st.selectbox("Who is sending the message?", ["junseopark719", "krx0011"])
new_message = st.text_area("Enter your message:")
if st.button("Add message"):
    psi = compute_psi(new_message)
    timestamp = datetime.datetime.now().isoformat()
    data.append({
        "timestamp": timestamp,
        "sender": sender,
        "text": new_message,
        "psi": psi
    })
    # Google Drive 연동 불가 → 저장 안내
    st.success(f"Message added! ψ(t) = {psi}")
    st.warning("Note: This update is local and not saved to Drive. Manual sync needed.")

# DataFrame 변환
if len(data) > 0:
    df = pd.DataFrame(data)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["index"] = range(len(df))
else:
    st.warning("No data available.")
    st.stop()

# 사용자 분리
junseo_df = df[df["sender"] == "junseopark719"]
kristina_df = df[df["sender"] == "krx0011"]

# 그래프
fig, ax = plt.subplots(figsize=(12, 6))
if not junseo_df.empty:
    ax.plot(junseo_df["index"], junseo_df["psi"], 'b-o', label="ψ_Junseo(t)")
if not kristina_df.empty:
    ax.plot(kristina_df["index"], kristina_df["psi"], 'r--o', label="ψ_Kristina(t)")
if not junseo_df.empty and not kristina_df.empty:
    min_len = min(len(junseo_df), len(kristina_df))
    x_vals = np.array(junseo_df["index"].iloc[:min_len])
    j_psi = np.array(junseo_df["psi"].iloc[:min_len])
    k_psi = np.array(kristina_df["psi"].iloc[:min_len])
    ax.fill_between(x_vals, j_psi, k_psi, color='gray', alpha=0.2, label="Δψ(t)")

ax.set_ylim(0, 1)
ax.set_title("ψ(t) Emotional-Cognitive Wave")
ax.set_xlabel("Message Index")
ax.set_ylabel("Wave Amplitude (ψ)")
ax.grid(True)
ax.legend()

st.pyplot(fig)
