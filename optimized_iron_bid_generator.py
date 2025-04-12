import streamlit as st
import pandas as pd
from io import StringIO

# Streamlit requires this first
st.set_page_config(layout="centered")

# Apply enhanced styling
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Rubik:wght@400;600&display=swap');

        .stApp {
            background: linear-gradient(to right, #f7f9fc, #e8f0ff);
            font-family: 'Rubik', sans-serif;
        }
        .header-bar {
            background-color: #003366;
            color: white;
            padding: 1rem 2rem;
            border-radius: 8px;
            margin-bottom: 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .header-bar h1 {
            margin: 0;
            font-size: 1.8rem;
        }
        .logo {
            height: 48px;
        }
        .stButton>button {
            background-color: #cc6600;
            color: white;
            font-weight: 600;
            border-radius: 8px;
            padding: 0.5em 1.2em;
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            background-color: #ff751a;
            box-shadow: 0 2px 6px rgba(0,0,0,0.15);
        }
        .stTextInput>div>input, .stNumberInput>div>input {
            background-color: #ffffff;
            border-radius: 6px;
            border: 1px solid #cccccc;
            padding: 0.4em 0.6em;
        }
        .stTabs [data-baseweb="tab"] {
            font-size: 16px;
            font-weight: 600;
            color: #004488;
        }
        .line-item-card {
            background-color: #ffffff;
            padding: 1.2em;
            margin-bottom: 1.5em;
            border-radius: 12px;
            box-shadow: 0 3px 12px rgba(0,0,0,0.07);
            transition: all 0.3s ease;
            border-left: 6px solid #cc6600;
        }
        .line-item-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 6px 16px rgba(0,0,0,0.1);
        }
    </style>
""", unsafe_allow_html=True)

# --- Top Header Bar ---
st.markdown("""
    <div class="header-bar">
        <h1>🛠️ Iron Plumbing PDF & Estimating Suite</h1>
        <img src="https://cdn-icons-png.flaticon.com/512/2965/2965567.png" class="logo" />
    </div>
""", unsafe_allow_html=True)

# --- Tab 3: Cost Estimator ---
def render_cost_estimator():
    st.header("🧮 Project Cost Estimator")

    if "cost_items" not in st.session_state:
        st.session_state.cost_items = [
            {"material_cost": 0.0, "labor_hours": 0.0, "labor_rate": 85.0, "margin_percent": 15.0, "final_price": 0.0}
        ]

    def calculate_final_price(item):
        labor_cost = item["labor_hours"] * item["labor_rate"]
        subtotal = item["material_cost"] + labor_cost
        return round(subtotal * (1 + item["margin_percent"] / 100), 2)

    def add_cost_item():
        st.session_state.cost_items.append(
            {"material_cost": 0.0, "labor_hours": 0.0, "labor_rate": 85.0, "margin_percent": 15.0, "final_price": 0.0}
        )

    st.write("Enter line items to estimate total project cost:")

    for i, item in enumerate(st.session_state.cost_items):
        with st.container():
            st.markdown(f'<div class="line-item-card">', unsafe_allow_html=True)
            st.subheader(f"Line Item {i + 1}")
            item["material_cost"] = st.number_input(f"📦 Material Cost ${i+1}", min_value=0.0, value=item["material_cost"], key=f"mat_{i}")
            item["labor_hours"] = st.number_input(f"🕒 Labor Hours {i+1}", min_value=0.0, value=item["labor_hours"], key=f"hrs_{i}")
            item["labor_rate"] = st.number_input(f"💰 Labor Rate ($/hr) {i+1}", min_value=0.0, value=item["labor_rate"], key=f"rate_{i}")
            item["margin_percent"] = st.number_input(f"📈 Target Margin % {i+1}", min_value=0.0, max_value=100.0, value=item["margin_percent"], key=f"margin_{i}")

            item["final_price"] = calculate_final_price(item)
            st.success(f"✅ Final Price: ${item['final_price']:,.2f}")
            st.markdown("</div>", unsafe_allow_html=True)

    st.button("➕ Add Line Item", on_click=add_cost_item)

    total_bid = sum(item["final_price"] for item in st.session_state.cost_items)
    st.markdown(f"## 🧾 Total Project Bid: **${total_bid:,.2f}**")

    if st.button("📤 Export to CSV"):
        output = StringIO()
        df = pd.DataFrame(st.session_state.cost_items)
        df.to_csv(output, index=False)
        st.success("✅ Export ready!")
        st.download_button("📥 Download CSV", data=output.getvalue(), file_name="iron_cost_estimate.csv", mime="text/csv")

# --- Main App Tabs ---
tab1, tab2, tab3 = st.tabs(["📄 Bid Generator", "📁 Dossier Generator", "🧮 Cost Estimator"])

# Tab 1 Placeholder (Bid Generator)
with tab1:
    st.info("Bid Generator goes here (integrate your existing bid generation logic).")

# Tab 2 Placeholder (Dossier Generator)
with tab2:
    st.info("Dossier Generator goes here (integrate your existing dossier generation logic).")

# Tab 3 Active (Cost Estimator)
with tab3:
    render_cost_estimator()


