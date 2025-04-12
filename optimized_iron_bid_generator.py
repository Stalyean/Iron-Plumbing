import streamlit as st
import pandas as pd
from io import StringIO, BytesIO
from fpdf import FPDF
from datetime import date

st.set_page_config(layout="centered")

# Styling and Header Bar
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Rubik:wght@400;600&display=swap');
        .stApp { background: linear-gradient(to right, #f7f9fc, #e8f0ff); font-family: 'Rubik', sans-serif; }
        .header-bar {
            background-color: #003366; color: white; padding: 1rem 2rem;
            border-radius: 8px; margin-bottom: 2rem; display: flex;
            justify-content: space-between; align-items: center;
        }
        .header-bar h1 { margin: 0; font-size: 1.8rem; }
        .logo { height: 48px; }
        .stButton>button {
            background-color: #cc6600; color: white; font-weight: 600;
            border-radius: 8px; padding: 0.5em 1.2em; transition: all 0.3s ease;
        }
        .stButton>button:hover {
            background-color: #ff751a; box-shadow: 0 2px 6px rgba(0,0,0,0.15);
        }
        .stTextInput>div>input, .stNumberInput>div>input {
            background-color: #ffffff; border-radius: 6px;
            border: 1px solid #cccccc; padding: 0.4em 0.6em;
        }
        .stTabs [data-baseweb="tab"] {
            font-size: 16px; font-weight: 600; color: #004488;
        }
        .line-item-card {
            background-color: #ffffff; padding: 1.2em; margin-bottom: 1.5em;
            border-radius: 12px; box-shadow: 0 3px 12px rgba(0,0,0,0.07);
            transition: all 0.3s ease; border-left: 6px solid #cc6600;
        }
        .line-item-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 6px 16px rgba(0,0,0,0.1);
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="header-bar">
        <h1>🛠️ Iron Plumbing PDF & Estimating Suite</h1>
        <img src="https://cdn-icons-png.flaticon.com/512/2965/2965567.png" class="logo" />
    </div>
""", unsafe_allow_html=True)

# --- Bid PDF Generator ---
def generate_bid_pdf(project, location, client, total, fixtures, terms, sig_date=None):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    today = date.today().strftime("%B %d, %Y")
    sig_date = sig_date or today
    pdf.cell(0, 10, f"Date: {today}", ln=True)
    pdf.cell(0, 10, f"Project: {project}", ln=True)
    pdf.cell(0, 10, f"Location: {location}", ln=True)
    pdf.cell(0, 10, f"Client: {client}", ln=True)
    pdf.cell(0, 10, f"Total Bid: ${total:,.2f}", ln=True)
    pdf.ln(5)
    pdf.set_font("Helvetica", style="B", size=12)
    pdf.cell(0, 10, "Scope of Work:", ln=True)
    pdf.set_font("Helvetica", size=11)
    for fixture in fixtures.splitlines():
        pdf.multi_cell(0, 8, f"- {fixture.strip()}")
    pdf.ln(3)
    pdf.set_font("Helvetica", style="B", size=12)
    pdf.cell(0, 10, "Terms:", ln=True)
    pdf.set_font("Helvetica", size=11)
    for term in terms.splitlines():
        pdf.multi_cell(0, 8, f"• {term.strip()}")
    pdf.ln(10)
    pdf.cell(0, 10, "Signature: _____________________", ln=True)
    pdf.cell(0, 10, f"Date: {sig_date}", ln=True)
    return BytesIO(pdf.output(dest='S').encode('latin1'))

# --- Dossier PDF Generator ---
def generate_dossier_pdf(project, location, client, fixtures):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    pdf.cell(0, 10, f"Project: {project}", ln=True)
    pdf.cell(0, 10, f"Location: {location}", ln=True)
    pdf.cell(0, 10, f"Client: {client}", ln=True)
    pdf.ln(5)
    pdf.set_font("Helvetica", style="B", size=12)
    pdf.cell(0, 10, "Fixture Summary:", ln=True)
    pdf.set_font("Helvetica", size=11)
    for line in fixtures.splitlines():
        pdf.multi_cell(0, 8, f"- {line.strip()}")
    return BytesIO(pdf.output(dest='S').encode('latin1'))

# --- Cost Estimator ---
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

# --- Tabs ---
tab1, tab2, tab3 = st.tabs(["📄 Bid Generator", "📁 Dossier Generator", "🧮 Cost Estimator"])

with tab1:
    st.header("📄 Bid Generator")
    project = st.text_input("Project Name")
    location = st.text_input("Location")
    client = st.text_input("Client / GC Name")
    bid_total = st.number_input("Total Bid Amount", min_value=0.0, step=100.0)
    fixtures = st.text_area("Fixture List (one per line)")
    terms = st.text_area("Terms", value="50% due at rough-in, 50% upon final inspection\nValid for 30 days from bid date")
    sig_date = st.text_input("Signature Date", value=date.today().strftime("%B %d, %Y"))
    if st.button("📄 Generate Bid PDF"):
        pdf_bytes = generate_bid_pdf(project, location, client, bid_total, fixtures, terms, sig_date)
        st.download_button("📥 Download Bid PDF", data=pdf_bytes, file_name="Iron_Bid.pdf")

with tab2:
    st.header("📁 Dossier Generator")
    project_d = st.text_input("Dossier Project Name")
    location_d = st.text_input("Dossier Location")
    client_d = st.text_input("Dossier Client")
    fixtures_d = st.text_area("Dossier Fixture List (one per line)")
    if st.button("📁 Generate Dossier PDF"):
        dossier_bytes = generate_dossier_pdf(project_d, location_d, client_d, fixtures_d)
        st.download_button("📥 Download Dossier PDF", data=dossier_bytes, file_name="Iron_Dossier.pdf")

with tab3:
    render_cost_estimator()



