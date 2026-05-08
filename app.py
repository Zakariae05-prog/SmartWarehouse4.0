import streamlit as st
import pandas as pd
import math
import random
import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LinearRegression

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="AI Smart Warehouse 4.0",
    layout="wide"
)

st.title("🏭 AI Smart Warehouse 4.0")
st.markdown("## Intelligent Logistics & Industry 4.0 Platform")

# =====================================================
# SESSION STATE
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

if "alerts" not in st.session_state:
    st.session_state.alerts = []

if "order_path" not in st.session_state:
    st.session_state.order_path = []

if "time_saved" not in st.session_state:
    st.session_state.time_saved = 0

if "distance_saved" not in st.session_state:
    st.session_state.distance_saved = 0

if "cost_saved" not in st.session_state:
    st.session_state.cost_saved = 0

if "co2_saved" not in st.session_state:
    st.session_state.co2_saved = 0

data = st.session_state.data

# =====================================================
# DISTANCE FUNCTION
# =====================================================
def distance(a, b):

    return math.sqrt(
        (a[0] - b[0])**2 +
        (a[1] - b[1])**2
    )

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
# AI PICKING OPTIMIZATION
# =====================================================
def optimize_path(order_list, df):

    current = (0, 0)

    remaining = order_list.copy()

    path = []

    while remaining:

        nearest = None
        min_distance = float("inf")

        for p in remaining:

            row = df[df["Product"] == p].iloc[0]

            pos = (row["X"], row["Y"])

            d = distance(current, pos)

            # penalty for heavy products
            if row["Weight"] > 20:
                d += 2

            if d < min_distance:

                min_distance = d

                nearest = p

        path.append(nearest)

        row = df[df["Product"] == nearest].iloc[0]

        current = (row["X"], row["Y"])

        remaining.remove(nearest)

    return path

# =====================================================
# DEMAND ANALYSIS
# =====================================================
def analyze_demand(history):

    demand = {}

    for p in history:

        demand[p] = demand.get(p, 0) + 1

    return demand

# =====================================================
# AI DYNAMIC LAYOUT
# =====================================================
def optimize_layout(df, demand):

    if not demand:
        return df

    sorted_products = sorted(
        demand.items(),
        key=lambda x: x[1],
        reverse=True
    )

    best_positions = [
        (0,0),
        (1,0),
        (0,1),
        (1,1),
        (2,0)
    ]

    df = df.copy()

    for i, (product, _) in enumerate(sorted_products):

        if i < len(best_positions):

            df.loc[
                df["Product"] == product,
                "X"
            ] = best_positions[i][0]

            df.loc[
                df["Product"] == product,
                "Y"
            ] = best_positions[i][1]

    return df

# =====================================================
# MACHINE LEARNING DEMAND PREDICTION
# =====================================================
def predict_demand(history, products):

    predictions = {}

    for product in products:

        occurrences = [
            1 if h == product else 0
            for h in history
        ]

        if len(occurrences) < 2:

            predictions[product] = random.randint(1, 5)

        else:

            X = np.array(
                range(len(occurrences))
            ).reshape(-1, 1)

            y = np.array(occurrences)

            model = LinearRegression()

            model.fit(X, y)

            future = np.array([
                [len(occurrences) + 1]
            ])

            pred = model.predict(future)[0]

            predictions[product] = round(
                max(pred * 10, 0),
                2
            )

    return predictions

# =====================================================
# PROFESSIONAL KPI
# =====================================================
st.subheader("📊 Professional Logistics KPI")

before_time = 120

after_time = max(
    before_time - st.session_state.time_saved,
    0
)

before_distance = 50

after_distance = max(
    before_distance -
    st.session_state.distance_saved,
    0
)

improvement = (
    (
        before_time - after_time
    ) / before_time
) * 100

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric(
    "⏱ Before AI",
    f"{before_time} sec"
)

col2.metric(
    "🤖 After AI",
    f"{round(after_time,2)} sec",
    delta=f"-{round(improvement,1)}%"
)

col3.metric(
    "📏 Distance Saved",
    f"{round(st.session_state.distance_saved,2)} m"
)

col4.metric(
    "💰 Cost Saved",
    f"{round(st.session_state.cost_saved,2)} €"
)

col5.metric(
    "🌱 CO₂ Reduced",
    f"{round(st.session_state.co2_saved,2)} kg"
)

st.dataframe(data)

# =====================================================
# SMART ORDER
# =====================================================
st.subheader("🛒 Smart Picking Order")

order = st.multiselect(
    "Select products",
    data["Product"].tolist()
)

if st.button("🚀 Generate AI Picking"):

    if not order:

        st.warning(
            "Select at least one product"
        )

    else:

        # Heavy products detection
        heavy_products = []

        for p in order:

            row = data[
                data["Product"] == p
            ].iloc[0]

            if row["Weight"] > 20:

                heavy_products.append(p)

        if heavy_products:

            st.warning(
                f"⚠ Heavy products detected : "
                f"{', '.join(heavy_products)}"
            )

            st.info(
                "🤖 AI recommends forklift assistance"
            )

        normal_path = order

        ai_path = optimize_path(
            order,
            data
        )

        normal_distance = total_distance(
            normal_path,
            data
        )

        ai_distance = total_distance(
            ai_path,
            data
        )

        distance_saved = (
            normal_distance -
            ai_distance
        )

        time_saved = distance_saved * 2

        cost_saved = distance_saved * 0.5

        co2_saved = distance_saved * 0.2

        st.session_state.order_path = ai_path

        st.session_state.distance_saved = (
            distance_saved
        )

        st.session_state.time_saved = (
            time_saved
        )

        st.session_state.cost_saved = (
            cost_saved
        )

        st.session_state.co2_saved = (
            co2_saved
        )

        st.success(
            "✅ AI Picking Optimized"
        )

        st.write(
            "### 🤖 AI Optimized Path"
        )

        st.write(
            " ➜ ".join(ai_path)
        )

        st.write(
            f"📏 Normal Distance : "
            f"{normal_distance}"
        )

        st.write(
            f"📏 AI Distance : "
            f"{ai_distance}"
        )

        st.write(
            f"⏱ Estimated Time Saved : "
            f"{round(time_saved,2)} sec"
        )

# =====================================================
# IOT SMART SCAN
# =====================================================
st.subheader("📡 IoT Smart Scan")

scan_product = st.selectbox(
    "Scan Product",
    data["Product"].tolist()
)

if st.button("📡 Scan"):

    row = data[
        data["Product"] == scan_product
    ].iloc[0]

    defect = (
        random.random() <
        row["Defect_rate"]
    )

    st.session_state.history.append(
        scan_product
    )

    if defect:

        alert = (
            f"❌ DEFECT DETECTED : "
            f"{scan_product}"
        )

        st.session_state.alerts.append(
            alert
        )

        st.error(alert)

    else:

        st.success(
            f"✅ {scan_product} Valid"
        )

        st.session_state.data.loc[
            st.session_state.data["Product"]
            == scan_product,
            "Stock"
        ] -= 1

# =====================================================
# AI LAYOUT OPTIMIZATION
# =====================================================
if st.button("🔄 AI Layout Optimization"):

    demand = analyze_demand(
        st.session_state.history
    )

    st.session_state.data = optimize_layout(
        st.session_state.data,
        demand
    )

    st.success(
        "🏭 Warehouse Automatically Reorganized"
    )

# =====================================================
# DEMAND ANALYSIS
# =====================================================
st.subheader("📈 Demand Analysis")

if st.session_state.history:

    demand = analyze_demand(
        st.session_state.history
    )

    st.bar_chart(demand)

else:

    st.info("No history yet")

# =====================================================
# AI DEMAND PREDICTION
# =====================================================
st.subheader("🧠 AI Demand Prediction")

predictions = predict_demand(
    st.session_state.history,
    data["Product"].tolist()
)

pred_df = pd.DataFrame({
    "Product": list(predictions.keys()),
    "Predicted Demand": list(
        predictions.values()
    )
})

st.dataframe(pred_df)

st.line_chart(
    pred_df.set_index("Product")
)

# =====================================================
# HEATMAP
# =====================================================
st.subheader("🔥 AI Warehouse Heatmap")

fig, ax = plt.subplots(
    figsize=(8,6)
)

history_demand = analyze_demand(
    st.session_state.history
)

for _, row in st.session_state.data.iterrows():

    demand_level = history_demand.get(
        row["Product"],
        1
    )

    ax.scatter(
        row["X"],
        row["Y"],
        s=700,
        c=demand_level,
        cmap="RdYlGn_r"
    )

    ax.text(
        row["X"],
        row["Y"],
        row["Product"],
        ha='center',
        va='center',
        fontsize=12
    )

ax.set_title(
    "AI Dynamic Warehouse Heatmap"
)

ax.grid(True)

st.pyplot(fig)

# =====================================================
# DIGITAL TWIN
# =====================================================
st.subheader("🛰 Digital Twin Warehouse")

fig2, ax2 = plt.subplots(
    figsize=(9,7)
)

for _, row in st.session_state.data.iterrows():

    ax2.scatter(
        row["X"],
        row["Y"],
        s=900
    )

    ax2.text(
        row["X"],
        row["Y"],
        f"{row['Product']}\nStock:{row['Stock']}",
        ha='center',
        va='center',
        fontsize=10
    )

if st.session_state.order_path:

    coords_x = [0]
    coords_y = [0]

    for p in st.session_state.order_path:

        row = st.session_state.data[
            st.session_state.data["Product"]
            == p
        ].iloc[0]

        coords_x.append(row["X"])
        coords_y.append(row["Y"])

    ax2.plot(
        coords_x,
        coords_y,
        linewidth=3
    )

ax2.set_title(
    "Warehouse Digital Twin"
)

ax2.grid(True)

st.pyplot(fig2)

# =====================================================
# UNEXPECTED EVENTS
# =====================================================
st.subheader(
    "⚠ Unexpected Industrial Events"
)

events = [
    "No issue",
    "Robot blocked",
    "Stock shortage",
    "Path congestion",
    "Machine failure"
]

event = random.choice(events)

if event == "No issue":

    st.success(
        "✅ Warehouse operating normally"
    )

elif event == "Robot blocked":

    st.error(
        "🚧 AGV Robot blocked"
    )

    st.info(
        "🤖 AI recalculates alternative route"
    )

elif event == "Stock shortage":

    st.error(
        "📦 Stock shortage detected"
    )

    st.info(
        "🤖 AI suggests replenishment"
    )

elif event == "Path congestion":

    st.warning(
        "🚶 Congested picking zone"
    )

    st.info(
        "🤖 AI reroutes operators"
    )

elif event == "Machine failure":

    st.error(
        "⚙ Conveyor failure detected"
    )

    st.info(
        "🤖 Predictive maintenance activated"
    )

# =====================================================
# PREDICTIVE MAINTENANCE
# =====================================================
st.subheader(
    "⚙ Predictive Maintenance"
)

temperature = random.randint(20, 80)

vibration = random.randint(10, 100)

humidity = random.randint(30, 90)

colA, colB, colC = st.columns(3)

colA.metric(
    "🌡 Temperature",
    f"{temperature} °C"
)

colB.metric(
    "📳 Vibration",
    vibration
)

colC.metric(
    "💧 Humidity",
    f"{humidity}%"
)

if temperature > 60:

    st.error(
        "⚠ High Temperature Detected"
    )

if vibration > 80:

    st.error(
        "⚠ Predictive Maintenance Required"
    )

# =====================================================
# AI RESILIENCE KPI
# =====================================================
st.subheader("🧠 AI Resilience KPI")

resilience_score = random.randint(
    85,
    99
)

st.progress(
    resilience_score / 100
)

st.write(
    f"AI System Resilience : "
    f"{resilience_score}%"
)

# =====================================================
# ALERTS
# =====================================================
st.subheader("🚨 Smart Alerts")

if st.session_state.alerts:

    for alert in st.session_state.alerts:

        st.warning(alert)

else:

    st.info("No alerts")

# =====================================================
# LAST AI PATH
# =====================================================
st.subheader("🚶 Last AI Path")

if st.session_state.order_path:

    st.write(
        " ➜ ".join(
            st.session_state.order_path
        )
    )

else:

    st.info("No path generated")if "data" not in st.session_state:

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
