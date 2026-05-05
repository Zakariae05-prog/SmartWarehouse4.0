import streamlit as st
import pandas as pd
import math
import random

st.title("🏭 Smart Warehouse 4.0 - AI Picking System")

# =========================
# 📊 DATA STOCK
# =========================
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame({
        "Product": ["A", "B", "C", "D", "E"],
        "X": [1, 5, 2, 8, 6],
        "Y": [1, 2, 6, 3, 7],
        "Stock": [10, 8, 15, 5, 12],
        "Defect_rate": [0.1, 0.05, 0.2, 0.08, 0.12]
    })

data = st.session_state.data

st.subheader("📊 Warehouse Stock")
st.dataframe(data)

# =========================
# 📦 ORDERS
# =========================
st.subheader("🛒 New Order")

order = st.multiselect(
    "Select products",
    data["Product"].tolist()
)

# =========================
# 📏 DISTANCE
# =========================
def distance(p1, p2):
    return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

# =========================
# 🚀 OPTIMIZATION (simple AI)
# =========================
def optimize_path(order_list, df):
    remaining = order_list.copy()
    path = []
    current = (0, 0)

    while remaining:
        nearest = None
        min_dist = float("inf")

        for p in remaining:
            row = df[df["Product"] == p].iloc[0]
            pos = (row["X"], row["Y"])
            dist = distance(current, pos)

            if dist < min_dist:
                min_dist = dist
                nearest = p

        path.append(nearest)
        current = (df[df["Product"] == nearest].iloc[0]["X"],
                   df[df["Product"] == nearest].iloc[0]["Y"])
        remaining.remove(nearest)

    return path

# =========================
# 📡 QR SCAN SIMULATION
# =========================
st.subheader("📡 QR Scan System")

scanned_product = st.selectbox("Scan product (simulate QR)", data["Product"].tolist())

def scan_product(product):
    # simulation defect detection
    row = data[data["Product"] == product].iloc[0]
    is_defect = random.random() < row["Defect_rate"]
    return is_defect

# =========================
# 🚀 PROCESS ORDER
# =========================
if st.button("🚀 Process Order & Optimize Picking"):

    if not order:
        st.warning("Select at least one product")
    else:
        path = optimize_path(order, data)

        st.success("✅ Optimized Picking Route Generated")

        st.write("📍 Operator Path:")
        st.write(" → ".join(path))

        st.session_state.current_order = path

# =========================
# 📡 SCAN VALIDATION
# =========================
if st.button("📡 Scan Product"):

    is_defect = scan_product(scanned_product)

    if is_defect:
        st.error(f"❌ {scanned_product} is DEFECTIVE!")

        st.warning("🚨 Alert sent to quality system")

    else:
        st.success(f"✅ {scanned_product} OK")

        # update stock
        data.loc[data["Product"] == scanned_product, "Stock"] -= 1
        st.session_state.data = data

# =========================
# 📊 DASHBOARD
# =========================
st.subheader("📊 Live Dashboard")

col1, col2, col3 = st.columns(3)

col1.metric("Total Stock", int(data["Stock"].sum()))
col2.metric("Products", len(data))
col3.metric("Avg Defect Rate", round(data["Defect_rate"].mean(), 2))

st.subheader("📦 Updated Stock")
st.dataframe(data)
