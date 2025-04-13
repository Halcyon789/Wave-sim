
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime
import time

# 올바르게 수정된 쿼리 파라미터 처리 코드
query_params = st.experimental_get_query_params()
current_user = query_params.get("user", ["guest"])[0]

# Shared log
@st.cache_data(show_spinner=False)
def get_shared_log():
    return []

if "shared_log" not in st.session_state:
    st.session_state.shared_log = get_shared_log()

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
st.title("ψ(t) Shared Emotional Resonance Chat")
st.caption("Real-time shared chat using stable query parameters and synced log.")

# Input UI
with st.container():
    st.markdown(f"**You are:** `{current_user}`")
    message = st.text_input("Your message:")
    if st.button("Send") and message.strip():
        st.session_state.shared_log.append({
            "user": current_user,
            "text": message,
            "timestamp": time.time(),
            "psi": compute_psi(message),
            "emotion": classify_emotion(message)
        })
        st.rerun()

# Dataframe
df = pd.DataFrame(st.session_state.shared_log)
if df.empty:
    st.info("No messages yet.")
    st.stop()

df["index"] = range(len(df))
df["time_str"] = df["timestamp"].apply(lambda ts: datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S'))

# Chat UI
st.markdown("---")
st.subheader("Live Chat")
for _, row in df.tail(30).iterrows():
    align = "left" if row["user"] != current_user else "right"
    bg = "#f1f0f0" if align == "left" else "#d1e7dd"
    block = f"""
    <div style='text-align:{align}; background:{bg}; padding:10px 15px;
        border-radius:15px; margin:5px; max-width:70%; display:inline-block'>
        <b>{row['user']}</b><br>
        {row['text']}<br>
        <small>ψ = {row['psi']} | {row['emotion']}</small><br>
        <small>{row['time_str']}</small>
    </div>
    """
    st.markdown(block, unsafe_allow_html=True)

# Visualization
users = df["user"].unique().tolist()
if len(users) < 2:
    st.warning("At least two users needed.")
    st.stop()

df_a = df[df["user"] == users[0]].reset_index(drop=True)
df_b = df[df["user"] == users[1]].reset_index(drop=True)

min_len = min(len(df_a), len(df_b))
psi_a = df_a["psi"].iloc[:min_len].astype(float).values
psi_b = df_b["psi"].iloc[:min_len].astype(float).values
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
