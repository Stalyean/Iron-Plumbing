import streamlit as st
from fpdf import FPDF
from datetime import date
import tempfile
import json
from io import BytesIO

# Brand colors
COPPER = (204, 102, 0)
RED = (204, 0, 0)
BLUE = (0, 102, 204)

# Custom PDF class with footer
class IronBidPDF(FPDF):
    def header(self):
        if getattr(self, 'logo_path', None):
            self.image(self.logo_path, x=10, y=10, w=40)
        self.set_xy(120, 10)
        self.set_font("Helvetica", 'B', 12)
        self.multi_cell(0, 8, "IRON PLUMBING SERVICES\nAmerican Fork, UT 84003\nIRONPLUMBINGUT@gmail.com\n801-895-5987", align='R')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", 'I', 9)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, "Iron Strength, Fluid Precision", align='C')

# Line drawing helper
def draw_line(pdf, color=COPPER):
    pdf.set_draw_color(*color)
    pdf.set_line_width(0.5)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)

# Section builder
def add_section(pdf, title, content_list, bullet_point="-", line_color=None):
    if line_color:
        draw_line(pdf, color=line_color)
    pdf.set_font("Helvetica", style="B", size=11)
    pdf.cell(0, 10, f"{title}:", ln=True)
    pdf.set_font("Helvetica", size=11)
    for item in content_list:
        pdf.multi_cell(0, 8, f"{bullet_point} {item}")
    pdf.ln(5)

# PDF generation logic
def generate_bid(project_name, location, client_name, bid_total, plumbing_fixtures, terms, logo_path=None, sig_date=None):
    today = date.today().strftime("%B %d, %Y")
    sig_date = sig_date or today
    pdf = IronBidPDF()
    pdf.logo_path = logo_path
    pdf.add_page()
    pdf.set_font("Helvetica", size=11)

    # Header Section
    pdf.set_font("Helvetica", style="B", size=11)
    pdf.cell(0, 10, f"Date: {today}", ln=True)
    pdf.cell(0, 10, f"Project: {project_name}", ln=True)
    pdf.cell(0, 10, f"Location: {location}", ln=True)
    pdf.cell(0, 10, f"Prepared For: {client_name}", ln=True)
    pdf.ln(5)

    # Scope
    pdf.set_font("Helvetica", style="BU", size=11)
    pdf.cell(0, 10, "SCOPE OF WORK - PLUMBING & GAS", ln=True)

    add_section(pdf, "PLUMBING", [
        "Furnish and install all rough-in and finish plumbing for:",
        *[f"  - {fixture}" for fixture in plumbing_fixtures],
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

    # Bid Total
    pdf.set_font("Helvetica", style="B", size=11)
    pdf.cell(0, 10, f"TOTAL BID: ${bid_total:,.2f}", ln=True)
    pdf.set_font("Helvetica", size=11)
    pdf.cell(0, 10, "(Includes labor, materials, and standard commercial fixtures)", ln=True)
    pdf.ln(5)

    # Terms
    add_section(pdf, "TERMS", terms)

    # Contact / Sign-off
    pdf.cell(0, 10, "Thank you for the opportunity to bid this project. We look forward to working with you.", ln=True)
    pdf.ln(5)
    add_section(pdf, "- Iron Plumbing Utah", [
        "Jerod Galyean",
        "Field Manager",
        "IRON PLUMBING SERVICES",
        "801-895-5987"
    ], bullet_point="")

    # Signature blocks
    add_section(pdf, "Authorized Signature", [
        "_________________________",
        "Signature",
        f"Date: {sig_date}"
    ])

    add_section(pdf, "Client/GC Approval", [
        "_________________________",
        "Client Signature",
        "Date: ___________________"
    ])

    pdf_buffer = BytesIO()
    pdf.output(pdf_buffer)
    pdf_buffer.seek(0)
    return pdf_buffer

# --- Streamlit App ---
st.title("Iron Plumbing Bid Generator (Branded + Autofill)")

# Sidebar logo upload
st.sidebar.subheader("Upload Your Logo")
uploaded_logo = st.sidebar.file_uploader("Upload Logo (Optional)", type=["png", "jpg", "jpeg"])

# Sidebar JSON uploader
st.sidebar.subheader("Upload JSON to Auto-fill")
uploaded_json = st.sidebar.file_uploader("Upload AI-Extracted JSON", type=["json"])

# Load JSON if present
autofill_data = {}
if uploaded_json:
    try:
        autofill_data = json.load(uploaded_json)
        st.sidebar.success("JSON loaded successfully!")
    except Exception as e:
        st.sidebar.error(f"Error loading JSON: {e}")

# Main form
project = st.text_input("Project Name", value=autofill_data.get("project_name", ""))
location = st.text_input("Project Location", value=autofill_data.get("location", ""))
client = st.text_input("Prepared For (GC/Client)", value=autofill_data.get("client_name", ""))
bid_total = st.number_input("Total Bid Amount", min_value=0.0, step=100.0, value=autofill_data.get("bid_total", 0.0))
fixtures = st.text_area("List each fixture on a new line", value="\n".join(autofill_data.get("plumbing_fixtures", [])))
terms_input = st.text_area("List terms (one per line)", value="\n".join(autofill_data.get("terms", [
    "50% due at rough-in, 50% upon final inspection",
    "Valid for 30 days from bid date",
    "Subject to change pending final site walk"
])))
sig_date = st.text_input("Signature Date (Optional)", value=date.today().strftime("%B %d, %Y"))

# Generate
if st.button("Generate Bid PDF"):
    fixture_list = [line.strip() for line in fixtures.split("\n") if line.strip()]
    terms_list = [line.strip() for line in terms_input.split("\n") if line.strip()]
    logo_path = None

    if uploaded_logo:
        logo_path = tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_logo.name.split('.')[-1]}").name
        with open(logo_path, "wb") as f:
            f.write(uploaded_logo.read())

    try:
        pdf_buffer = generate_bid(project, location, client, bid_total, fixture_list, terms_list, logo_path, sig_date)
        st.download_button("Download Bid PDF", pdf_buffer, file_name="Iron_Bid.pdf")
    except Exception as e:
        st.error(f"An error occurred while generating the PDF: {e}")
