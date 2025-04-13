import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json

st.set_page_config(layout="wide")
st.title("ψ(t) Emotional-Cognitive Wave Visualization")

try:
    with open("message_log.json", "r") as f:
        data = json.load(f)
    df = pd.DataFrame(data)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["index"] = range(len(df))
except:
    st.warning("Could not load message_log.json.")
    st.stop()

junseo_df = df[df["sender"] == "junseopark719"]
kristina_df = df[df["sender"] == "krx0011"]

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
