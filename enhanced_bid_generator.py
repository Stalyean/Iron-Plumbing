import streamlit as st
from fpdf import FPDF
from datetime import date
import tempfile
from io import BytesIO

# Enhanced IronBidPDF Class
class IronBidPDF(FPDF):
    def header(self):
        if getattr(self, 'logo_path', None):
            self.image(self.logo_path, x=10, y=10, w=40)
        self.set_xy(120, 10)
        self.set_font("Helvetica", 'B', 12)
        self.multi_cell(0, 8, "IRON PLUMBING SERVICES\nAmerican Fork, UT 84003\nIRONPLUMBINGUT@gmail.com\n801-895-5987", align='R')
        self.ln(10)

def add_section(pdf, title, content_list, bullet_point="-"):
    """
    Utility function to add a titled section to the PDF.
    """
    pdf.set_font("Helvetica", style="B", size=11)
    pdf.cell(0, 10, f"{title}:", ln=True)
    pdf.set_font("Helvetica", size=11)
    for item in content_list:
        pdf.multi_cell(0, 8, f"{bullet_point} {item}")
    pdf.ln(5)

def generate_bid(project_name, location, client_name, bid_total, plumbing_fixtures, terms, logo_path=None):
    """
    Generates a professional bid PDF.
    """
    today = date.today().strftime("%B %d, %Y")
    pdf = IronBidPDF()
    pdf.logo_path = logo_path
    pdf.add_page()
    pdf.set_font("Helvetica", size=11)

    # Project Details
    pdf.set_font("Helvetica", style="B", size=11)
    pdf.cell(0, 10, f"Date: {today}", ln=True)
    pdf.cell(0, 10, f"Project: {project_name}", ln=True)
    pdf.cell(0, 10, f"Location: {location}", ln=True)
    pdf.cell(0, 10, f"Prepared For: {client_name}", ln=True)
    pdf.ln(5)

    # Scope of Work
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
    ])
    add_section(pdf, "GAS", [
        "Install gas line to water heater location (if gas WH is selected)",
        "Test and pressure-check line to code",
        "Coordinate with utility for tie-in"
    ])

    # Inclusions and Exclusions
    add_section(pdf, "INCLUSIONS", [
        "Commercial-grade fixtures (e.g., Kohler/Delta/Sloan or equivalent)",
        "All hangers, straps, valves, and related materials",
        "Coordination with GC and other trades",
        "As-built drawings and final inspection walk"
    ])
    add_section(pdf, "EXCLUSIONS", [
        "Core drilling through structural concrete (unless noted)",
        "Fire sprinklers, HVAC, or low-voltage",
        "Permit fees (assumed by GC)",
        "Trenching or tie-ins beyond 10’ of building"
    ])

    # Total Bid
    pdf.set_font("Helvetica", style="B", size=11)
    pdf.cell(0, 10, f"TOTAL BID: ${bid_total:,.2f}", ln=True)
    pdf.set_font("Helvetica", size=11)
    pdf.cell(0, 10, "(Includes labor, materials, and standard commercial fixtures)", ln=True)
    pdf.ln(5)

    # Terms
    add_section(pdf, "TERMS", terms)

    # Thank You Note and Contact Info
    pdf.cell(0, 10, "Thank you for the opportunity to bid this project. We look forward to working with you.", ln=True)
    pdf.ln(5)
    add_section(pdf, "- Iron Plumbing Utah", [
        "Jerod Galyean",
        "Field Manager",
        "IRON PLUMBING SERVICES",
        "801-895-5987"
    ], bullet_point="")

    # Signature Section
    add_section(pdf, "Authorized Signature", ["_________________________", "Signature", f"Date: {today}"], bullet_point="")
    add_section(pdf, "Client/GC Approval", ["_________________________", "Client Signature", "Date: ___________________"], bullet_point="")

    # Save to a temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(temp_file.name)
    return temp_file.name

# Streamlit UI
st.title("Iron Plumbing Bid Generator (Enhanced)")
st.write("Fill out the form below to generate a professional bid PDF.")

# Sidebar for Logo Upload
st.sidebar.subheader("Upload Your Logo")
uploaded_logo = st.sidebar.file_uploader("Upload Logo (Optional)", type=["png", "jpg", "jpeg"])

# Bid Details Form
project = st.text_input("Project Name")
location = st.text_input("Project Location")
client = st.text_input("Prepared For (GC/Client)")
bid_total = st.number_input("Total Bid Amount", min_value=0.0, step=100.0)

# Plumbing Fixtures Input
st.subheader("Plumbing Fixtures")
fixtures = st.text_area("List each fixture on a new line")

# Terms Input
st.subheader("Terms")
terms_input = st.text_area("List terms (one per line)", value="50% due at rough-in, 50% upon final inspection\nValid for 30 days from bid date\nSubject to change pending final site walk")

# Generate Button
if st.button("Generate Bid PDF"):
    # Process Input
    fixture_list = [line.strip() for line in fixtures.split("\n") if line.strip()]
    terms_list = [line.strip() for line in terms_input.split("\n") if line.strip()]
    logo_path = None

    # Save uploaded logo if provided
    if uploaded_logo:
        logo_path = tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_logo.name.split('.')[-1]}").name
        with open(logo_path, "wb") as f:
            f.write(uploaded_logo.read())

    # Generate PDF
    try:
        file_path = generate_bid(project, location, client, bid_total, fixture_list, terms_list, logo_path)
        with open(file_path, "rb") as f:
            st.download_button("Download Bid PDF", f, file_name="Bid_Document.pdf")
    except Exception as e:
        st.error(f"An error occurred while generating the PDF: {e}")
