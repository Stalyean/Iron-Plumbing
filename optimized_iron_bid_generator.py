import streamlit as st
import pandas as pd
import json
from io import BytesIO
from datetime import date
from fpdf import FPDF
from tempfile import NamedTemporaryFile

st.set_page_config(layout="centered")

# Sidebar: Logo, JSON Upload, and AI Plan Parser
st.sidebar.header("🧰 Project Setup")
logo_file = st.sidebar.file_uploader("📤 Upload Logo for PDFs", type=["png", "jpg", "jpeg"])
uploaded_json = st.sidebar.file_uploader("📥 Load Auto-Fill JSON", type=["json"])


autofill_data = {}
if uploaded_json:
    try:
        autofill_data = json.load(uploaded_json)
        st.sidebar.success("✅ JSON Loaded!")
    except Exception as e:
        st.sidebar.error(f"❌ Failed to load JSON: {e}")

logo_path = None
if logo_file:
    tmp = NamedTemporaryFile(delete=False, suffix="." + logo_file.name.split(".")[-1])
    tmp.write(logo_file.read())
    tmp.close()
    logo_path = tmp.name

# Dossier PDF Generator
def generate_dossier_pdf(project, location, client, fixtures, logo_path=None):
    pdf = FPDF()
    pdf.add_page()
    if logo_path:
        pdf.image(logo_path, x=10, y=8, w=40)
        pdf.set_y(30)
    pdf.set_font("Helvetica", size=12)
    pdf.cell(0, 10, f"Project: {project}", ln=True)
    pdf.cell(0, 10, f"Location: {location}", ln=True)
    pdf.cell(0, 10, f"Client: {client}", ln=True)
    pdf.ln(5)
    pdf.set_font("Helvetica", style="B", size=12)
    pdf.cell(0, 10, "Fixture Summary:", ln=True)
    pdf.set_font("Helvetica", size=11)
    for fixture in fixtures.splitlines():
        pdf.multi_cell(0, 8, f"- {fixture.strip()}")
    return BytesIO(pdf.output(dest='S').encode('latin1'))

# Cost Estimator Logic
def render_cost_estimator():
    st.header("🧮 Project Cost Estimator")
    if "cost_items" not in st.session_state:
        st.session_state.cost_items = []
    def calculate_final_price(item):
        labor_cost = item["labor_hours"] * item["labor_rate"]
        subtotal = item["material_cost"] + labor_cost
        return round(subtotal * (1 + item["margin_percent"] / 100), 2)
    def add_cost_item():
        st.session_state.cost_items.append({
            "material_cost": 0.0,
            "labor_hours": 0.0,
            "labor_rate": 85.0,
            "margin_percent": 15.0,
            "final_price": 0.0
        })
    st.button("➕ Add Line Item", on_click=add_cost_item)
    total_bid = 0.0
    for i, item in enumerate(st.session_state.cost_items):
        with st.expander(f"🔧 Line Item {i + 1}", expanded=True):
            item["material_cost"] = st.number_input(f"📦 Material Cost {i+1}", value=item["material_cost"], key=f"mat_{i}")
            item["labor_hours"] = st.number_input(f"🕒 Labor Hours {i+1}", value=item["labor_hours"], key=f"hrs_{i}")
            item["labor_rate"] = st.number_input(f"💰 Labor Rate {i+1}", value=item["labor_rate"], key=f"rate_{i}")
            item["margin_percent"] = st.number_input(f"📈 Margin % {i+1}", value=item["margin_percent"], key=f"margin_{i}")
            item["final_price"] = calculate_final_price(item)
            st.success(f"💲 Final Price: ${item['final_price']:,.2f}")
        total_bid += item["final_price"]
    st.subheader(f"🧾 Total Estimated Bid: ${total_bid:,.2f}")

# Bid PDF Generator
def generate_bid_pdf(project, location, client, total, fixtures, terms, sig_date=None, logo_path=None):
    pdf = FPDF()
    pdf.add_page()
    if logo_path:
        pdf.image(logo_path, x=10, y=8, w=40)
        pdf.set_y(30)
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
        ascii_bullet = "-" if not term.startswith("  ") else "  -"
        pdf.multi_cell(0, 6, f"{ascii_bullet} {term.strip()}")
    pdf.ln(10)
    pdf.cell(0, 10, "Signature: _____________________", ln=True)
    pdf.cell(0, 10, f"Date: {sig_date}", ln=True)
    return BytesIO(pdf.output(dest='S').encode('latin1'))

# --- Tabs ---
tab1, tab2, tab3 = st.tabs(["📄 Bid Generator", "📁 Dossier Generator", "🧮 Cost Estimator"])

# --- Tab 1: Bid Generator
with tab1:
    st.title("📄 Iron Plumbing Bid Generator")

    st.header("🧾 Project Information")
    project = st.text_input("Project Name", value=autofill_data.get("project_info", {}).get("project_name", ""))
    location = st.text_input("Project Address", value=autofill_data.get("project_info", {}).get("project_address", ""))
    project_type = st.selectbox("Project Type", ["New Build", "Remodel", "Addition", "TI", "Other"],
        index=["New Build", "Remodel", "Addition", "TI", "Other"].index(autofill_data.get("project_info", {}).get("project_type", "New Build")))
    scope_description = st.text_area("Scope of Work Requested", value=autofill_data.get("project_info", {}).get("scope_description", ""))
    square_footage = st.text_input("Square Footage", value=autofill_data.get("project_info", {}).get("square_footage", ""))

    st.header("👤 Client/Contact Info")
    company = st.text_input("Company Name", value=autofill_data.get("client_info", {}).get("company", ""))
    contact_name = st.text_input("Client/Contact Name", value=autofill_data.get("client_info", {}).get("contact_name", ""))
    phone = st.text_input("Phone Number", value=autofill_data.get("client_info", {}).get("phone", ""))
    email = st.text_input("Email Address", value=autofill_data.get("client_info", {}).get("email", ""))
    preferred_contact = st.selectbox("Preferred Contact Method", ["Phone", "Email", "Text", "Other"],
        index=["Phone", "Email", "Text", "Other"].index(autofill_data.get("client_info", {}).get("preferred_contact", "Phone")))

    st.header("📦 Fixtures")
    fixtures = st.text_area("Fixture List (one per line)", value=autofill_data.get("bid_summary", {}).get("fixture_list", ""))

    st.header("📑 Bid Summary")
    bid_total = st.number_input("Total Bid Amount", min_value=0.0, step=100.0,
        value=autofill_data.get("bid_summary", {}).get("bid_total", 0.0))
    default_terms = autofill_data.get("bid_summary", {}).get("terms", "Estimate Validity: This estimate is valid for 30 days from the issue date.")
    terms = st.text_area("Terms", value=st.session_state.get("terms", default_terms), height=300, key="terms")
    if st.button("🔁 Reset to Default Terms"):
        st.session_state["terms"] = default_terms
        st.experimental_rerun()
    sig_date = st.text_input("Signature Date", value=autofill_data.get("bid_summary", {}).get("signature_date", date.today().strftime("%B %d, %Y")))

    if st.button("📄 Generate Bid PDF"):
        pdf = generate_bid_pdf(project, location, contact_name, bid_total, fixtures, terms, sig_date, logo_path)
        st.download_button("📥 Download Bid PDF", pdf, file_name="Iron_Bid.pdf")

# --- Tab 2: Dossier Generator
with tab2:
    st.header("📁 Generate Dossier PDF")
    dossier_project = st.text_input("Dossier Project Name", value=project)
    dossier_location = st.text_input("Dossier Location", value=location)
    dossier_client = st.text_input("Dossier Client", value=contact_name)
    dossier_fixtures = st.text_area("Dossier Fixture List", value=fixtures)
    if st.button("📄 Generate Dossier PDF"):
        dossier_pdf = generate_dossier_pdf(dossier_project, dossier_location, dossier_client, dossier_fixtures, logo_path)
        st.download_button("📥 Download Dossier PDF", dossier_pdf, file_name="Iron_Dossier.pdf")

# --- Tab 3: Cost Estimator
with tab3:
    render_cost_estimator()
    pdf = generate_bid_pdf(project, location, contact_name, bid_total, fixtures, terms, sig_date, logo_path)
    st.download_button("📥 Download Bid PDF", pdf, file_name="Iron_Bid.pdf")

