import streamlit as st
import json
from fpdf import FPDF
from datetime import date
import tempfile
from io import BytesIO

# Enhanced IronBidPDF Class with Courier Font
class IronBidPDF(FPDF):
    def header(self):
        if getattr(self, 'logo_path', None):
            self.image(self.logo_path, x=10, y=10, w=40)
        self.set_xy(120, 10)
        self.set_font("Courier", 'B', 12)  # Use Courier Bold for header
        self.multi_cell(0, 8, "IRON PLUMBING SERVICES\nAmerican Fork, UT 84003\nIRONPLUMBINGUT@gmail.com\n801-895-5987", align='R')
        self.ln(10)

# Generate Bid Function
def generate_bid(project, location, client, bid_total, fixture_list, terms_list, logo_path=None):
    try:
        pdf = IronBidPDF()
        
        if logo_path:
            pdf.logo_path = logo_path

        pdf.add_page()
        pdf.set_font("Courier", size=12)  # Use Courier font

        # Add Project Details
        pdf.cell(200, 10, txt=f"Project: {project}", ln=True, align='L')
        pdf.cell(200, 10, txt=f"Location: {location}", ln=True, align='L')
        pdf.cell(200, 10, txt=f"Prepared For: {client}", ln=True, align='L')
        pdf.ln(10)

        # Add Fixtures
        pdf.set_font("Courier", 'B', size=12)
        pdf.cell(200, 10, txt="Fixtures:", ln=True, align='L')
        pdf.set_font("Courier", size=12)
        for fixture in fixture_list:
            pdf.cell(200, 10, txt=f"- {fixture}", ln=True, align='L')

        # Add Bid Total
        pdf.ln(5)
        pdf.set_font("Courier", 'B', size=12)
        pdf.cell(200, 10, txt=f"Total Bid Amount: ${bid_total:.2f}", ln=True, align='R')

        # Add Terms
        pdf.ln(10)
        pdf.set_font("Courier", size=12)
        pdf.cell(200, 10, txt="Terms and Conditions:", ln=True, align='L')
        pdf.set_font("Courier", size=10)
        for term in terms_list:
            pdf.multi_cell(0, 10, txt=f"- {term}")

        # Save to in-memory buffer
        pdf_buffer = BytesIO()
        pdf.output(pdf_buffer)
        pdf_buffer.seek(0)
        return pdf_buffer

    except Exception as e:
        # Log the error for debugging purposes and re-raise the exception
        print(f"Error in generate_bid function: {e}")
        raise

# Streamlit UI
st.title("Iron Plumbing Bid Generator (Enhanced)")
st.write("Fill out the form below to generate a professional bid PDF.")

# Sidebar for Logo Upload
st.sidebar.subheader("Upload Your Logo")
uploaded_logo = st.sidebar.file_uploader("Upload Logo (Optional)", type=["png", "jpg", "jpeg"])

# Section for Importing AI-Extracted Data
st.subheader("Import AI-Extracted Data")
uploaded_data_file = st.file_uploader("Upload AI-Extracted Data (JSON)", type=["json"])

if uploaded_data_file:
    try:
        # Parse the uploaded JSON file
        uploaded_data = json.load(uploaded_data_file)
        st.success("AI-Extracted Data Uploaded Successfully!")

        # Pre-fill fields based on uploaded data
        project = st.text_input("Project Name", value=uploaded_data.get("project_name", ""))
        location = st.text_input("Project Location", value=uploaded_data.get("location", ""))
        client = st.text_input("Prepared For (GC/Client)", value=uploaded_data.get("client_name", ""))
        bid_total = st.number_input("Total Bid Amount", min_value=0.0, step=100.0, value=uploaded_data.get("bid_total", 0.0))
        fixtures = st.text_area("List each fixture on a new line", value="\n".join(uploaded_data.get("plumbing_fixtures", [])))
        terms_input = st.text_area("List terms (one per line)", value="\n".join(uploaded_data.get("terms", [])))
    except Exception as e:
        st.error(f"Failed to process uploaded data: {e}")
else:
    # Default values if no file is uploaded
    project = st.text_input("Project Name")
    location = st.text_input("Project Location")
    client = st.text_input("Prepared For (GC/Client)")
    bid_total = st.number_input("Total Bid Amount", min_value=0.0, step=100.0)
    fixtures = st.text_area("List each fixture on a new line")
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
        pdf_buffer = generate_bid(project, location, client, bid_total, fixture_list, terms_list, logo_path)
        st.download_button("Download Bid PDF", pdf_buffer, file_name="Bid_Document.pdf")
    except Exception as e:
        st.error(f"An error occurred while generating the PDF: {e}")
