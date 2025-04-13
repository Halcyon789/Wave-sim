
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
import requests
import datetime
from collections import Counter

st.set_page_config(layout="wide")
st.title("ψ(t) 감정-의식 대화 시뮬레이터")

drive_url = "https://drive.google.com/uc?id=1-DZnniFffJJucJkw6Wx4TSmEZpjiahiz"
backend_url = "https://9030-34-80-88-205.ngrok-free.app/log_message"

def classify_emotion(text):
    emo_map = {
        "love": "사랑", "miss": "그리움", "beautiful": "감탄",
        "happy": "행복", "wow": "감동", "fun": "재미",
        "sad": "슬픔", "alone": "외로움", "scared": "두려움",
        "hurt": "상처", "hate": "분노",
        "why": "혼란", "what": "탐색"
    }
    for word, emotion in emo_map.items():
        if word in text.lower():
            return emotion
    return "중립"

emotion_emojis = {
    "사랑": "❤️", "그리움": "🤍", "감탄": "🧡", "행복": "💛",
    "감동": "💜", "재미": "💚", "슬픔": "💙", "외로움": "🩶",
    "두려움": "🖤", "상처": "🩸", "분노": "🔥",
    "혼란": "❓", "탐색": "🔍", "중립": "⚪"
}

def compute_psi(text):
    emotional_keywords = list(emotion_emojis.keys())
    E = sum(emotion in classify_emotion(text) for emotion in emotional_keywords)
    L = min(len(text) / 100, 1.0)
    S = 0.7 if "?" in text else 0.3
    return round(0.5 * E / len(emotional_keywords) + 0.2 * L + 0.3 * S, 2)

def save_to_backend(sender, text, psi):
    try:
        requests.post(backend_url, json={"sender": sender, "text": text, "psi": psi})
    except:
        pass

try:
    res = requests.get(drive_url)
    data = json.loads(res.content)
except:
    data = []

data = [d for d in data if "timestamp" in d and d["timestamp"]]

with st.container():
    st.markdown("### 새로운 메시지")
    col1, col2 = st.columns([2, 6])
    with col1:
        sender = st.selectbox("보낸 사람", ["junseopark719", "krx0011"])
    with col2:
        new_message = st.text_input("메시지 입력", placeholder="Type your feeling...")

    if st.button("보내기"):
        psi = compute_psi(new_message)
        emotion = classify_emotion(new_message)
        timestamp = datetime.datetime.now().isoformat()
        data.append({
            "timestamp": timestamp,
            "sender": sender,
            "text": new_message,
            "psi": psi,
            "emotion": emotion
        })
        save_to_backend(sender, new_message, psi)
        st.success(f"ψ = {psi}, 감정 = {emotion} 저장됨.")

df = pd.DataFrame(data)
if "emotion" not in df.columns:
    df["emotion"] = df["text"].apply(classify_emotion)
df["timestamp"] = pd.to_datetime(df["timestamp"], errors='coerce')
df = df.dropna(subset=["timestamp"])
df["index"] = range(len(df))

junseo_df = df[df["sender"] == "junseopark719"]
kristina_df = df[df["sender"] == "krx0011"]

if not junseo_df.empty and not kristina_df.empty:
    min_len = min(len(junseo_df), len(kristina_df))
    delta_psi = np.abs(junseo_df["psi"].iloc[:min_len].values - kristina_df["psi"].iloc[:min_len].values)
    avg_resonance = np.round(1 - np.mean(delta_psi), 2)
    emoji = "💞" if avg_resonance > 0.85 else "🌫️" if avg_resonance < 0.6 else "🔄"
    st.markdown(f"### 공명 지수: **{avg_resonance * 100:.1f}%** {emoji}")

st.markdown("### 대화 흐름 (텔레그램 스타일)")

for _, row in df.tail(15).iterrows():
    align = "left" if row["sender"] == "junseopark719" else "right"
    bubble_color = "#e3f2fd" if align == "left" else "#ffe0b2"
    emotion_tag = f"{emotion_emojis.get(row['emotion'], '⚪')} {row['emotion']}"
    style = f"text-align:{align}; background-color:{bubble_color}; padding:10px 15px; border-radius:15px; margin:5px; max-width:70%; display:inline-block"
    html = f"<div style='{style}'><b>{row['sender']}</b><br>{row['text']}<br><small>ψ={row['psi']} | {emotion_tag}</small></div>"
    st.markdown(html, unsafe_allow_html=True)

st.markdown("### 감정 기반 ψ(t) 시각화")
fig, ax = plt.subplots(figsize=(12, 6))
for sender_id in ["junseopark719", "krx0011"]:
    subset = df[df["sender"] == sender_id]
    for i, row in subset.iterrows():
        color = "gray" if row["emotion"] not in emotion_emojis else None
        ax.scatter(row["index"], row["psi"], color=color, label=row["emotion"] if i == 0 else "", s=80, alpha=0.8, edgecolors='k')

if not junseo_df.empty and not kristina_df.empty:
    min_len = min(len(junseo_df), len(kristina_df))
    x_vals = np.array(junseo_df["index"].iloc[:min_len])
    j_psi = np.array(junseo_df["psi"].iloc[:min_len])
    k_psi = np.array(kristina_df["psi"].iloc[:min_len])
    ax.fill_between(x_vals, j_psi, k_psi, color='gray', alpha=0.2, label="Δψ(t)")

ax.set_ylim(0, 1)
ax.set_xlabel("메시지 순서")
ax.set_ylabel("ψ(t)")
ax.set_title("감정 기반 ψ(t) 시각화")
ax.grid(True)
ax.legend(loc="lower right", fontsize="small")
st.pyplot(fig)

st.markdown("### 감정 통계")
emotion_count = Counter(df["emotion"])
emotion_df = pd.DataFrame.from_dict(emotion_count, orient='index').reset_index()
emotion_df.columns = ["감정", "빈도수"]
st.bar_chart(emotion_df.set_index("감정"))
