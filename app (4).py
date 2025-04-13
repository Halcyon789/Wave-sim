
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
import os
import datetime
from collections import Counter

# Path for message log
LOG_PATH = "message_log.json"

# Load or initialize message log
if os.path.exists(LOG_PATH):
    with open(LOG_PATH, "r") as f:
        message_log = json.load(f)
else:
    message_log = []

# Simulated session user (in production, replace with actual auth)
current_user = st.experimental_user.get("username", "junseo" if len(message_log) % 2 == 0 else "kristina")

# Define emotion keywords and emojis
emotion_map = {
    "love": "Love ❤️", "miss": "Longing 🤍", "beautiful": "Admiration 🧡",
    "happy": "Happiness 💛", "fun": "Fun 💚", "wow": "Amazement 💜",
    "sad": "Sadness 💙", "alone": "Loneliness 🤎", "scared": "Fear 🖤",
    "hurt": "Hurt 🩸", "hate": "Anger 🔥", "why": "Confusion ❓", "what": "Exploration 🔍"
}

def classify_emotion(text):
    for keyword, label in emotion_map.items():
        if keyword in text.lower():
            return label
    return "Neutral ⚪"

def compute_psi(text):
    return min(1.0, len(text) / 100)

# Layout
st.set_page_config(layout="wide")
st.title("ψ(t) Emotional Resonance Chat")
st.caption("Real-time cognitive-emotional visualization between two people")

# Input section
with st.container():
    st.markdown(f"**You are:** `{current_user}`")
    message = st.text_input("Your message:")
    if st.button("Send") and message.strip():
        psi = compute_psi(message)
        emotion = classify_emotion(message)
        message_log.append({
            "user": current_user,
            "text": message,
            "timestamp": datetime.datetime.now().isoformat(),
            "psi": psi,
            "emotion": emotion
        })
        with open(LOG_PATH, "w") as f:
            json.dump(message_log, f, indent=2)
        st.experimental_rerun()

# DataFrame from messages
df = pd.DataFrame(message_log)
if df.empty:
    st.info("No messages yet.")
    st.stop()

df["timestamp"] = pd.to_datetime(df["timestamp"])
df["index"] = range(len(df))

# Show chat UI
st.markdown("---")
st.subheader("Live Chat")

for _, row in df.tail(30).iterrows():
    align = "left" if row["user"] != current_user else "right"
    bg = "#f1f0f0" if align == "left" else "#d1e7dd"
    content = f"""
    <div style='text-align:{align}; background:{bg}; padding:10px 15px;
        border-radius:15px; margin:5px; max-width:70%; display:inline-block'>
        <b>{row['user']}</b><br>
        {row['text']}<br>
        <small>ψ = {row['psi']} | {row['emotion']}</small><br>
        <small>{row['timestamp'].strftime('%H:%M:%S')}</small>
    </div>
    """
    st.markdown(content, unsafe_allow_html=True)

# Split users
users = df["user"].unique().tolist()
if len(users) < 2:
    st.warning("At least two participants are needed for resonance visualization.")
    st.stop()

df_a = df[df["user"] == users[0]].reset_index(drop=True)
df_b = df[df["user"] == users[1]].reset_index(drop=True)

# Resonance calculation
min_len = min(len(df_a), len(df_b))
psi_diff = abs(df_a["psi"].iloc[:min_len].values - df_b["psi"].iloc[:min_len].values)
resonance_score = 1 - np.mean(psi_diff)
emoji = "💞" if resonance_score > 0.85 else "🔁" if resonance_score > 0.6 else "🌫️"
st.markdown(f"### Resonance Index: **{resonance_score * 100:.1f}%** {emoji}")

# ψ(t) Graph
st.subheader("ψ(t) Wave Visualization")
fig, ax = plt.subplots()
ax.plot(df_a["index"], df_a["psi"], 'b-o', label=f"ψ_{users[0]}")
ax.plot(df_b["index"], df_b["psi"], 'r--o', label=f"ψ_{users[1]}")
ax.fill_between(range(min_len), df_a["psi"].iloc[:min_len], df_b["psi"].iloc[:min_len], color="gray", alpha=0.3, label="Δψ")
ax.set_ylim(0, 1)
ax.set_xlabel("Message Index")
ax.set_ylabel("Wave Amplitude ψ(t)")
ax.legend()
st.pyplot(fig)

# Emotion frequency
st.subheader("Emotion Statistics")
emotion_labels = [classify_emotion(t) for t in df["text"]]
emotion_count = pd.Series(emotion_labels).value_counts()
st.bar_chart(emotion_count)
