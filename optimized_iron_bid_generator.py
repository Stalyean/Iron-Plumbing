import streamlit as st
import pandas as pd
import json
from datetime import date
from io import StringIO, BytesIO
import tempfile
import os
from fpdf import FPDF

# --- Constants ---
COPPER = (204, 102, 0)
RED = (204, 0, 0)
BLUE = (0, 102, 204)

# --- PDF Helpers ---
def sanitize_text(text):
    return text.replace("’", "'").replace("“", '"').replace("”", '"')

def draw_line(pdf, color=COPPER):
    pdf.set_draw_color(*color)
    pdf.set_line_width(0.5)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)

def add_section(pdf, title, content_list, bullet_point="-", line_color=None):
    if line_color:
        draw_line(pdf, color=line_color)
    pdf.set_font("Helvetica", style="B", size=11)
    pdf.cell(0, 10, sanitize_text(f"{title}:"), ln=True)
    pdf.set_font("Helvetica", style="", size=11)
    for item in content_list:
        pdf.multi_cell(0, 8, sanitize_text(f"{bullet_point} {item}"))
    pdf.ln(5)

# --- PDF Class ---
class IronPDF(FPDF):
    def header(self):
        if getattr(self, 'logo_path', None) and os.path.exists(self.logo_path):
            self.image(self.logo_path, x=10, y=10, w=40)
        self.set_xy(120, 10)
        self.set_font("Helvetica", style="B", size=12)
        self.multi_cell(0, 8, sanitize_text("IRON PLUMBING SERVICES\nAmerican Fork, UT 84003\nIRONPLUMBINGUT@gmail.com\n801-895-5987"), align='R')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", style="I", size=9)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, sanitize_text("Iron Strength, Fluid Precision"), align='C')

# --- Bid PDF Generator ---
def generate_bid_pdf(project, location, client, total, fixtures, terms, logo_path=None, sig_date=None):
    today = date.today().strftime("%B %d, %Y")
    sig_date = sig_date or today
    pdf = IronPDF()
    pdf.logo_path = logo_path
    pdf.add_page()

    pdf.set_font("Helvetica", style="B", size=11)
    pdf.cell(0, 10, f"Date: {today}", ln=True)
    pdf.cell(0, 10, f"Project: {project}", ln=True)
    pdf.cell(0, 10, f"Location: {location}", ln=True)
    pdf.cell(0, 10, f"Prepared For: {client}", ln=True)
    pdf.ln(5)

    pdf.set_font("Helvetica", style="BU", size=11)
    pdf.cell(0, 10, "SCOPE OF WORK - PLUMBING & GAS", ln=True)

    add_section(pdf, "PLUMBING", [
        "Furnish and install all rough-in and finish plumbing for:",
        *[f"  - {f}" for f in fixtures],
        "Provide and install water heater (electric or gas)",
        "Distribution of hot and cold lines throughout building",
        "DWV (drain, waste, vent) system per code",
        "ADA-compliant fixtures throughout",
        "Final fixture connection and system testing"
    ], line_color=BLUE)

    add_section(pdf, "GAS", [
        "Install gas line to water heater location (if gas WH is selected)",
        "Test and pressure-check line to code",
        "Coordinate with utility for tie-in"
    ], line_color=RED)

    add_section(pdf, "INCLUSIONS", [
        "Commercial-grade fixtures (e.g., Kohler/Delta/Sloan or equivalent)",
        "All hangers, straps, valves, and related materials",
        "Coordination with GC and other trades",
        "As-built drawings and final inspection walk"
    ], line_color=COPPER)

    add_section(pdf, "EXCLUSIONS", [
        "Core drilling through structural concrete (unless noted)",
        "Fire sprinklers, HVAC, or low-voltage",
        "Permit fees (assumed by GC)",
        "Trenching or tie-ins beyond 10’ of building"
    ])

    pdf.set_font("Helvetica", style="B", size=11)
    pdf.cell(0, 10, f"TOTAL BID: ${total:,.2f}", ln=True)
    pdf.set_font("Helvetica", style="", size=11)
    pdf.cell(0, 10, "(Includes labor, materials, and standard commercial fixtures)", ln=True)
    pdf.ln(5)

    add_section(pdf, "TERMS", terms)
    pdf.cell(0, 10, "Thank you for the opportunity to bid this project. We look forward to working with you.", ln=True)
    pdf.ln(5)

    add_section(pdf, "- Iron Plumbing Utah", [
        "Jerod Galyean",
        "Field Manager",
        "IRON PLUMBING SERVICES",
        "801-895-5987"
    ], bullet_point="")

    add_section(pdf, "Authorized Signature", ["_________________________", "Signature", f"Date: {sig_date}"])
    add_section(pdf, "Client/GC Approval", ["_________________________", "Client Signature", "Date: ___________________"])
    return BytesIO(pdf.output(dest='S').encode('latin1'))

# --- Dossier PDF Generator ---
def generate_dossier_pdf(project, location, client, fixtures, contact=None, logo_path=None):
    pdf = IronPDF()
    pdf.logo_path = logo_path
    pdf.add_page()
    pdf.set_font("Helvetica", style="B", size=14)
    pdf.cell(0, 10, f"PROJECT DOSSIER: {project}", ln=True)
    pdf.set_font("Helvetica", style="", size=12)
    pdf.cell(0, 10, f"Location: {location}", ln=True)
    pdf.cell(0, 10, f"Prepared For: {client}", ln=True)
    pdf.ln(10)

    draw_line(pdf, color=BLUE)
    add_section(pdf, "Fixture Summary", fixtures, bullet_point="-", line_color=RED)

    if contact:
        add_section(pdf, "Primary Contact", [
            contact.get("name", "N/A"),
            contact.get("role", "N/A"),
            contact.get("phone", "N/A"),
            contact.get("email", "N/A")
        ], bullet_point="")

    draw_line(pdf, color=COPPER)
    pdf.cell(0, 10, "Additional documentation available upon request.", ln=True)

    return BytesIO(pdf.output(dest='S').encode('latin1'))

# --- Cost Estimator Tab ---
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

    for i, item in enumerate(st.session_state.cost_items):
        st.subheader(f"Line Item {i + 1}")
        item["material_cost"] = st.number_input(f"Material Cost ${i+1}", min_value=0.0, value=item["material_cost"], key=f"mat_{i}")
        item["labor_hours"] = st.number_input(f"Labor Hours {i+1}", min_value=0.0, value=item["labor_hours"], key=f"hrs_{i}")
        item["labor_rate"] = st.number_input(f"Labor Rate ($/hr) {i+1}", min_value=0.0, value=item["labor_rate"], key=f"rate_{i}")
        item["margin_percent"] = st.number_input(f"Target Margin % {i+1}", min_value=0.0, max_value=100.0, value=item["margin_percent"], key=f"margin_{i}")

        item["final_price"] = calculate_final_price(item)
        st.success(f"Final Price: ${item['final_price']:,.2f}")
        st.markdown("---")

    st.button("➕ Add Line Item", on_click=add_cost_item)

    total_bid = sum(item["final_price"] for item in st.session_state.cost_items)
    st.markdown(f"## 🧾 Total Project Bid: **${total_bid:,.2f}**")

    if st.button("📤 Export to CSV"):
        output = StringIO()
        df = pd.DataFrame(st.session_state.cost_items)
        df.to_csv(output, index=False)
        st.download_button("Download CSV", data=output.getvalue(), file_name="iron_cost_estimate.csv", mime="text/csv")

# --- Streamlit UI ---
st.set_page_config(layout="centered")
st.title("Iron Plumbing PDF & Estimating Suite")

tab1, tab2, tab3 = st.tabs(["📄 Bid Generator", "📁 Dossier Generator", "🧮 Cost Estimator"])

# Shared Sidebar
with st.sidebar:
    st.subheader("Upload Files")
    uploaded_logo = st.file_uploader("Company Logo", type=["png", "jpg", "jpeg"])
    uploaded_json = st.file_uploader("Auto-Fill JSON", type=["json"])
    autofill_data = {}
    if uploaded_json:
        try:
            autofill_data = json.load(uploaded_json)
            st.success("JSON Loaded!")
        except Exception as e:
            st.error(f"Error loading JSON: {e}")
    logo_path = None
    if uploaded_logo:
        temp_logo = tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_logo.name.split('.')[-1]}")
        logo_path = temp_logo.name
        temp_logo.write(uploaded_logo.read())
        temp_logo.close()

# --- Tab 1: Bid Generator ---
with tab1:
    st.header("📄 Generate Bid PDF")
    project = st.text_input("Project Name", value=autofill_data.get("project_name", ""))
    location = st.text_input("Location", value=autofill_data.get("location", ""))
    client = st.text_input("Client / GC Name", value=autofill_data.get("client_name", ""))
    bid_total = st.number_input("Total Bid Amount", min_value=0.0, step=100.0, value=autofill_data.get("bid_total", 0.0))
    fixtures = st.text_area("Fixture List", value="\n".join(autofill_data.get("plumbing_fixtures", [])))
    terms = st.text_area("Terms", value="\n".join(autofill_data.get("terms", [
        "50% due at rough-in, 50% upon final inspection",
        "Valid for 30 days from bid date"
    ])))
    sig_date = st.text_input("Signature Date", value=date.today().strftime("%B %d, %Y"))

    if st.button("Generate Bid PDF"):
        try:
            pdf = generate_bid_pdf(project, location, client, bid_total,
                                   [f.strip() for f in fixtures.splitlines() if f.strip()],
                                   [t.strip() for t in terms.splitlines() if t.strip()],
                                   logo_path, sig_date)
            st.download_button("Download Bid PDF", pdf, file_name="Iron_Bid.pdf")
        except Exception as e:
            st.error(f"Error generating PDF: {e}")

# --- Tab 2: Dossier Generator ---
with tab2:
    st.header("📁 Generate Project Dossier")
    project_d = st.text_input("Dossier Project Name", value=autofill_data.get("project_name", ""))
    location_d = st.text_input("Dossier Location", value=autofill_data.get("location", ""))
    client_d = st.text_input("Dossier Client", value=autofill_data.get("client_name", ""))
    fixtures_d = st.text_area("Dossier Fixture List", value="\n".join(autofill_data.get("plumbing_fixtures", [])))
    contact_d = autofill_data.get("contact", {
        "name": "Jerod Galyean",
        "role": "Field Manager",
        "phone": "801-895-5987",
        "email": "ironplumbingut@gmail.com"
    })

    if st.button("Generate Dossier PDF"):
        try:
            pdf = generate_dossier_pdf(project_d, location_d, client_d,
                                       [f.strip() for f in fixtures_d.splitlines() if f.strip()],
                                       contact_d, logo_path)
            st.download_button("Download Dossier PDF", pdf, file_name="Iron_Dossier.pdf")
        except Exception as e:
            st.error(f"Error generating dossier: {e}")

# --- Tab 3 ---
with tab3:
    render_cost_estimator()

