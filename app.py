
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
import os
import datetime
from collections import Counter

LOG_PATH = "message_log.json"
if os.path.exists(LOG_PATH):
    with open(LOG_PATH, "r") as f:
        message_log = json.load(f)
else:
    message_log = []

current_user = st.experimental_user.get("username", "junseo" if len(message_log) % 2 == 0 else "kristina")

emotion_map = {
    "love": "Love ❤️", "miss": "Longing 🤍", "beautiful": "Admiration 🧡",
    "happy": "Happiness 💛", "fun": "Fun 💚", "wow": "Amazement 💜",
    "sad": "Sadness 💙", "alone": "Loneliness 🤎", "scared": "Fear 🖤",
    "hurt": "Hurt 🩸", "hate": "Anger 🔥", "why": "Confusion ❓", "what": "Exploration 🔍"
}

def classify_emotion(text):
    for k, v in emotion_map.items():
        if k in text.lower():
            return v
    return "Neutral ⚪"

def compute_psi(text):
    return min(1.0, len(text) / 100)

st.set_page_config(layout="wide")
st.title("ψ(t) Emotional Resonance Chat")
st.caption("Real-time cognitive-emotional visualization between two people")

with st.container():
    st.markdown(f"**You are:** `{current_user}`")
    message = st.text_input("Your message:")
    if st.button("Send") and message.strip():
        psi = compute_psi(message)
        emotion = classify_emotion(message)
        timestamp = datetime.datetime.now().isoformat()
        message_log.append({
            "user": current_user,
            "text": message,
            "timestamp": timestamp,
            "psi": psi,
            "emotion": emotion
        })
        with open(LOG_PATH, "w") as f:
            json.dump(message_log, f, indent=2)
        st.experimental_rerun()

df = pd.DataFrame(message_log)
if df.empty:
    st.info("No messages yet.")
    st.stop()

df["timestamp"] = pd.to_datetime(df["timestamp"], errors='coerce')
df["index"] = range(len(df))
df["psi"] = df["psi"].fillna(df["text"].apply(compute_psi))
df["emotion"] = df["emotion"].fillna(df["text"].apply(classify_emotion))

st.markdown("---")
st.subheader("Live Chat")
for _, row in df.tail(30).iterrows():
    align = "left" if row["user"] != current_user else "right"
    bg = "#f1f0f0" if align == "left" else "#d1e7dd"
    ts_raw = row["timestamp"]
    if isinstance(ts_raw, str):
        try:
            ts_dt = datetime.datetime.fromisoformat(ts_raw)
            time_str = ts_dt.strftime('%H:%M:%S')
        except:
            time_str = ts_raw[-8:]
    else:
        time_str = ts_raw.strftime('%H:%M:%S')

    block = f"""
    <div style='text-align:{align}; background:{bg}; padding:10px 15px;
        border-radius:15px; margin:5px; max-width:70%; display:inline-block'>
        <b>{row['user']}</b><br>
        {row['text']}<br>
        <small>ψ = {row['psi']} | {row['emotion']}</small><br>
        <small>{time_str}</small>
    </div>
    """
    st.markdown(block, unsafe_allow_html=True)

users = df["user"].unique().tolist()
if len(users) < 2:
    st.warning("At least two users needed for resonance.")
    st.stop()

df_a = df[df["user"] == users[0]].reset_index(drop=True)
df_b = df[df["user"] == users[1]].reset_index(drop=True)

min_len = min(len(df_a), len(df_b))
psi_a = df_a["psi"].iloc[:min_len].values
psi_b = df_b["psi"].iloc[:min_len].values
psi_diff = abs(psi_a - psi_b)
resonance_score = 1 - np.mean(psi_diff)
emoji = "💞" if resonance_score > 0.85 else "🔁" if resonance_score > 0.6 else "🌫️"
st.markdown(f"### Resonance Index: **{resonance_score * 100:.1f}%** {emoji}")

st.subheader("ψ(t) Wave Visualization")
fig, ax = plt.subplots()
ax.plot(df_a["index"], df_a["psi"], 'b-o', label=f"ψ_{users[0]}")
ax.plot(df_b["index"], df_b["psi"], 'r--o', label=f"ψ_{users[1]}")
ax.fill_between(range(min_len), psi_a, psi_b, color="gray", alpha=0.3, label="Δψ")
ax.set_ylim(0, 1)
ax.set_xlabel("Message Index")
ax.set_ylabel("Wave Amplitude ψ(t)")
ax.legend()
st.pyplot(fig)

st.subheader("Emotion Statistics")
emotion_count = pd.Series(df["emotion"]).value_counts()
emotion_df = emotion_count.reset_index()
emotion_df.columns = ["Emotion", "Count"]
st.bar_chart(emotion_df.set_index("Emotion"))
