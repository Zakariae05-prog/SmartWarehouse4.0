import streamlit as st
import pandas as pd
import numpy as np
import math
import random
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans

# =====================================================
# CONFIG
# =====================================================
st.set_page_config(page_title="Smart Warehouse AI 4.0", layout="wide")

st.title("🏭 Smart Warehouse AI 4.0 - Industrial Intelligence System")

# =====================================================
# DATA INIT
# =====================================================
if "data" not in st.session_state:

    st.session_state.data = pd.DataFrame({
        "Product": ["A", "B", "C", "D", "E"],
        "X": [3, 5, 2, 8, 6],
        "Y": [1, 2, 6, 3, 7],
        "Stock": [20, 15, 30, 12, 18],
        "Weight": [5, 25, 8, 40, 12],
        "Defect_rate": [0.1, 0.05, 0.2, 0.08, 0.12]
    })

if "history" not in st.session_state:
    st.session_state.history = []

if "order_path" not in st.session_state:
    st.session_state.order_path = []

if "time_saved" not in st.session_state:
    st.session_state.time_saved = 0

if "distance_saved" not in st.session_state:
    st.session_state.distance_saved = 0

data = st.session_state.data

# =====================================================
# DATA QUALITY
# =====================================================
def clean_data(df):

    df = df.dropna()
    df = df[df["Stock"] >= 0]

    return df

data = clean_data(data)

# =====================================================
# DISTANCE
# =====================================================
def distance(a, b):
    return math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)

# =====================================================
# HEAVY PRODUCT PENALTY
# =====================================================
def heavy_penalty(row):

    if row["Weight"] > 20:
        return 3
    elif row["Weight"] > 10:
        return 1.5
    return 1

# =====================================================
# TOTAL DISTANCE
# =====================================================
def total_distance(path, df):

    current = (0, 0)
    total = 0

    for p in path:

        row = df[df["Product"] == p].iloc[0]
        pos = (row["X"], row["Y"])

        total += distance(current, pos)

        current = pos

    return round(total, 2)

# =====================================================
# AI PICKING
# =====================================================
def optimize_path(order, df):

    current = (0, 0)
    remaining = order.copy()
    path = []

    while remaining:

        best = None
        min_d = float("inf")

        for p in remaining:

            row = df[df["Product"] == p].iloc[0]
            pos = (row["X"], row["Y"])

            d = distance(current, pos) * heavy_penalty(row)

            if d < min_d:
                min_d = d
                best = p

        path.append(best)

        current = (
            df[df["Product"] == best]["X"].values[0],
            df[df["Product"] == best]["Y"].values[0]
        )

        remaining.remove(best)

    return path

# =====================================================
# CLUSTER SCALABILITY
# =====================================================
def cluster_layout(df):

    kmeans = KMeans(n_clusters=2, n_init=10)

    df["Zone"] = kmeans.fit_predict(df[["X", "Y"]])

    return df

data = cluster_layout(data)

# =====================================================
# KPI DASHBOARD
# =====================================================
st.subheader("📊 KPI Performance (Before vs After AI)")

before_time = 120
before_distance = 50

after_time = max(before_time - st.session_state.time_saved, 0)
after_distance = max(before_distance - st.session_state.distance_saved, 0)

gain = ((before_time - after_time) / before_time) * 100

col1, col2, col3, col4 = st.columns(4)

col1.metric("⏱ Before", f"{before_time} sec")
col2.metric("🤖 After", f"{after_time:.1f} sec", delta=f"-{gain:.1f}%")
col3.metric("📏 Distance Saved", f"{st.session_state.distance_saved:.1f}")
col4.metric("📈 Efficiency", f"{gain:.1f}%")

# =====================================================
# ORDER INPUT
# =====================================================
order = st.multiselect("Select Products", data["Product"].tolist())

if st.button("🚀 Run AI Optimization"):

    if order:

        path = optimize_path(order, data)

        dist = total_distance(path, data)

        base_dist = total_distance(order, data)

        st.session_state.distance_saved = base_dist - dist
        st.session_state.time_saved = (base_dist - dist) * 2

        st.session_state.order_path = path

        st.success("AI Optimization Completed")

        st.write("Optimized Path:", " → ".join(path))

# =====================================================
# SCAN SIMULATION
# =====================================================
st.subheader("📡 IoT Scan")

product = st.selectbox("Scan Product", data["Product"])

if st.button("Scan"):

    st.session_state.history.append(product)

    row = data[data["Product"] == product].iloc[0]

    if random.random() < row["Defect_rate"]:
        st.error("❌ Defective Product")
    else:
        st.success("✅ OK")

# =====================================================
# DEMAND ANALYSIS
# =====================================================
st.subheader("📊 Demand Analysis")

if st.session_state.history:

    demand = pd.Series(st.session_state.history).value_counts()

    st.bar_chart(demand)

# =====================================================
# EVENT SIMULATION
# =====================================================
st.subheader("⚠ System Events")

events = ["none", "robot_blocked", "stock_out", "congestion"]

event = random.choice(events)

st.write("Event:", event)

if event == "robot_blocked":
    st.warning("Robot blocked → rerouting")
elif event == "stock_out":
    st.error("Stock shortage detected")
elif event == "congestion":
    st.warning("Warehouse congestion detected")
else:
    st.success("Normal operation")

# =====================================================
# WAREHOUSE VISUALIZATION
# =====================================================
st.subheader("🗺 Warehouse Layout")

fig, ax = plt.subplots()

for _, row in data.iterrows():

    ax.scatter(row["X"], row["Y"], s=400)
    ax.text(row["X"], row["Y"], row["Product"], ha="center")

if st.session_state.order_path:

    x, y = [0], [0]

    for p in st.session_state.order_path:

        r = data[data["Product"] == p].iloc[0]

        x.append(r["X"])
        y.append(r["Y"])

    ax.plot(x, y)

st.pyplot(fig)

# =====================================================
# RESILIENCE SCORE
# =====================================================
st.subheader("🧠 AI Resilience")

score = random.randint(85, 99)

st.progress(score/100)
st.write(f"System Resilience: {score}%")
