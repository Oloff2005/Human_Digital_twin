from pathlib import Path

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from hdt.engine.simulator import Simulator
from hdt.config_loader import load_units_config
from hdt.inputs.input_parser import InputParser
from hdt.inputs.signal_normalizer import SignalNormalizer

PACKAGE_ROOT = Path(__file__).resolve().parent.parent
PROJECT_ROOT = PACKAGE_ROOT.parent

CONFIG_PATH = PACKAGE_ROOT / "config" / "units_config_active.yaml"
MAPPING_PATH = PACKAGE_ROOT / "config" / "wearable_mapping.json"
SAMPLE_INPUT = PROJECT_ROOT / "data" / "sample_inputs.json"

# ---------------------------------------------------------------------------
# Session initialization
# ---------------------------------------------------------------------------
if "simulator" not in st.session_state:
    config = load_units_config(str(CONFIG_PATH))
    parser = InputParser(str(MAPPING_PATH))
    parsed = parser.parse(str(SAMPLE_INPUT))
    signals = SignalNormalizer().normalize(parsed)
    st.session_state.simulator = Simulator(config=config, wearable_inputs=signals, verbose=False)
    st.session_state.config = config
    st.session_state.parsed_signals = parsed
    st.session_state.history = []
    st.session_state.metrics = {
        "glucose": [],
        "cortisol": [],
        "heart_rate": [],
        "sleep_quality": [],
        "glycogen": [],
        "sleep_drive": [],
    }

sim = st.session_state.simulator
config = st.session_state.config

# ---------------------------------------------------------------------------
# Sidebar Inputs
# ---------------------------------------------------------------------------
st.sidebar.header("Lifestyle Inputs")
carbs = st.sidebar.number_input("Carbs (g)", min_value=0.0, step=1.0, key="carbs")
fat = st.sidebar.number_input("Fat (g)", min_value=0.0, step=1.0, key="fat")
protein = st.sidebar.number_input("Protein (g)", min_value=0.0, step=1.0, key="protein")
sleep_hours = st.sidebar.number_input("Sleep duration (hours)", min_value=0.0, step=0.5, key="sleep")
intensity = st.sidebar.selectbox(
    "Workout intensity",
    ["None", "Light", "Moderate", "Intense"],
    key="intensity",
)
submitted = st.sidebar.button("Submit")
time_window = st.sidebar.slider(
    "History window (hours)", min_value=1, max_value=24, value=12, step=1
)
# ---------------------------------------------------------------------------
# Simulation step on submit
# ---------------------------------------------------------------------------
if submitted:
    level_map = {
        "None": "rest",
        "Light": "rest",
        "Moderate": "moderate",
        "Intense": "high",
    }
    activity_level = level_map.get(intensity, "rest")

    external = {
        "meal": {"carbs": carbs, "fat": fat, "protein": protein},
        "hours_awake": max(0.0, 24 - sleep_hours),
        "activity_level": activity_level,
    }

    sim.step(external)
    snapshot = sim.history[-1]
    st.session_state.history.append(snapshot)
    st.session_state.current_state = {name: unit.get_state() for name, unit in sim.units.items()}

    # Derived metrics
    glucose = snapshot.get("Liver", {}).get("liver_glucose", 0.0)
    cortisol = min(1.0, snapshot.get("BrainController", {}).get("stress_level", 0.0) * config.get("brain", {}).get("cortisol_threshold", 1.0))
    heart_rate = st.session_state.parsed_signals.get("BrainController", {}).get("heart_rate", 0) * 100
    sleep_quality = (1 - snapshot.get("SleepRegulationCenter", {}).get("sleep_drive", 0.0)) * 100
    glycogen = snapshot.get("Storage", {}).get("storage_glycogen", 0.0)
    sleep_drive = snapshot.get("SleepRegulationCenter", {}).get("sleep_drive", 0.0)

    st.session_state.metrics["glucose"].append(glucose)
    st.session_state.metrics["cortisol"].append(cortisol)
    st.session_state.metrics["heart_rate"].append(heart_rate)
    st.session_state.metrics["sleep_quality"].append(sleep_quality)
    st.session_state.metrics["glycogen"].append(glycogen)
    st.session_state.metrics["sleep_drive"].append(sleep_drive)

# ---------------------------------------------------------------------------
# Display current state
# ---------------------------------------------------------------------------
st.title("Human Digital Twin Dashboard")

if st.session_state.metrics["glucose"]:
    last_idx = -1
    st.subheader("Current Internal State")
    st.metric("Glucose", f"{st.session_state.metrics['glucose'][last_idx]:.2f}")
    st.metric("Cortisol", f"{st.session_state.metrics['cortisol'][last_idx]:.2f}")
    st.metric("Heart Rate", f"{st.session_state.metrics['heart_rate'][last_idx]:.0f}")
    st.metric("Sleep Quality", f"{st.session_state.metrics['sleep_quality'][last_idx]:.1f}")

    glycogen_level = st.session_state.metrics["glycogen"][last_idx]
    max_gly = config.get("storage", {}).get("max_glycogen", 1.0)
    st.subheader("Energy Reserves")
    st.progress(min(1.0, glycogen_level / max_gly))

    circadian_val = 1.0 - st.session_state.metrics["sleep_drive"][last_idx]
    st.subheader("Circadian Rhythm")
    st.progress(max(0.0, min(1.0, circadian_val)))

    st.subheader("Lifestyle Recommendations")
    recs = st.session_state.history[-1].get("recommendations", [])
    for rec in recs:
        st.write("-", rec)

    st.subheader("Trends")
    df = pd.DataFrame(st.session_state.metrics)
    df_window = df.tail(time_window)
    st.line_chart(df_window[["glucose", "heart_rate", "cortisol", "glycogen"]])
else:
    st.write("Enter inputs and submit to run the simulation.")
