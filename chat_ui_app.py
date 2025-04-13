import streamlit as st
import json
import matplotlib.pyplot as plt
import os
import datetime
import pandas as pd

LOG_PATH = "message_log.json"
if os.path.exists(LOG_PATH):
    with open(LOG_PATH, "r") as f:
        message_log = json.load(f)
else:
    message_log = []

# Simulated session-based user identification
current_user = st.experimental_user.get("username", "guest")

st.title("Emotional-Cognitive Wave Chat")
st.markdown("Chat and visualize ψ(t) with dynamic emotional awareness")

message = st.text_input("Your message:")
if st.button("Send") and message:
    message_log.append({
        "user": current_user,
        "text": message,
        "timestamp": datetime.datetime.now().isoformat()
    })
    with open(LOG_PATH, "w") as f:
        json.dump(message_log, f, indent=2)
    st.experimental_rerun()

# Display chat-like UI
st.markdown("---")
st.subheader("Chat")
for msg in reversed(message_log[-30:]):
    align = "left" if msg["user"] != current_user else "right"
    color = "#f1f0f0" if align == "left" else "#d1e7dd"
    st.markdown(f"""
    <div style='text-align:{align}; background-color:{color}; padding:10px 15px; 
        border-radius:15px; margin:5px; max-width:70%; display:inline-block'>
        <b>{msg['user']}</b><br>
        {msg['text']}<br>
        <small>{msg['timestamp'].split('T')[1][:8]}</small>
    </div>
    """, unsafe_allow_html=True)

# ψ(t) Calculation
if message_log:
    df = pd.DataFrame(message_log)
    df["psi"] = df["text"].apply(lambda x: min(1.0, len(x) / 100))
    user_a = df[df.user == df.user.unique()[0]]
    user_b = df[df.user == df.user.unique()[1]] if len(df.user.unique()) > 1 else pd.DataFrame()

    st.subheader("ψ(t) Emotional-Cognitive Wave")
    fig, ax = plt.subplots()
    ax.plot(user_a.index, user_a["psi"], label=f"ψ_{user_a.user.iloc[0]}", color="blue", marker="o")
    if not user_b.empty:
        ax.plot(user_b.index, user_b["psi"], label=f"ψ_{user_b.user.iloc[0]}", color="red", marker="o", linestyle="dashed")
        delta = abs(user_a["psi"].reset_index(drop=True) - user_b["psi"].reset_index(drop=True))
        ax.fill_between(range(len(delta)), 0, delta[:len(user_a)], color='gray', alpha=0.3, label="Δψ")
    ax.set_xlabel("Message Index")
    ax.set_ylabel("Wave Amplitude ψ(t)")
    ax.set_ylim(0, 1)
    ax.legend()
    st.pyplot(fig)

    if not user_b.empty:
        mean_delta = delta.mean()
        st.metric(label="Resonance Δψ(t)", value=f"{1 - mean_delta:.2f}")
