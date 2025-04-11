import streamlit as st
from fpdf import FPDF
from datetime import date
import tempfile
import json
from io import BytesIO
import os

# --- Constants ---
COPPER = (204, 102, 0)
RED = (204, 0, 0)
BLUE = (0, 102, 204)

# --- Helpers ---
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

    # ✅ CORRECT OUTPUT TO MEMORY
    pdf_bytes = pdf.output(dest='S').encode('latin1')
    return BytesIO(pdf_bytes)

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
    add_section(pdf, "Fixture Summary", fixtures, bullet_point="•", line_color=RED)

    if contact:
        add_section(pdf, "Primary Contact", [
            contact.get("name", "N/A"),
            contact.get("role", "N/A"),
            contact.get("phone", "N/A"),
            contact.get("email", "N/A")
        ], bullet_point="")

    draw_line(pdf, color=COPPER)
    pdf.cell(0, 10, "Additional documentation available upon request.", ln=True)

    # ✅ CORRECT OUTPUT TO MEMORY
    pdf_bytes = pdf.output(dest='S').encode('latin1')
    return BytesIO(pdf_bytes)

# --- Streamlit UI ---
st.set_page_config(layout="centered")
st.title("Iron Plumbing PDF Generator")

tab1, tab2 = st.tabs(["📄 Bid Generator", "📁 Dossier Generator"])

# Sidebar shared inputs
with st.sidebar:
    st.subheader("Upload Files")
    uploaded_logo = st.file_uploader("Company Logo", type=["png", "jpg", "jpeg"])
    uploaded_json = st.file_uploader("Auto-Fill JSON", type=["json"])

# Load JSON
autofill_data = {}
if uploaded_json:
    try:
        autofill_data = json.load(uploaded_json)
        st.sidebar.success("JSON Loaded!")
    except Exception as e:
        st.sidebar.error(f"Error loading JSON: {e}")

# Save logo temporarily
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
