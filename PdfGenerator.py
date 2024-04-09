import streamlit as st
import pandas as pd
from fpdf import FPDF
import os
import zipfile
import base64

def generate_pdf(df):
    pdf_files = []  # List to store the names of the generated PDF files
    # Group by name and iterate over groups
    for name, group in df.groupby('name'):
        # Create a new PDF file for each user
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=10)

        # Add a title
        pdf.cell(200, 10, f"Details of : {name}", ln=True, align='C')
        pdf.ln(5)

        # Add a table header
        pdf.set_fill_color(200, 220, 255)
        for column in group.columns:
            pdf.cell(40, 10, column, 1, 0, 'C', 1)
        pdf.ln()

        # Add data to the table
        for _, row in group.iterrows():
            for column in group.columns:
                pdf.cell(40, 10, str(row[column]), 1, 0, 'C')
            pdf.ln()

        # Save the PDF file
        pdf_filename = f"user_{name}_info.pdf"
        pdf.output(pdf_filename)
        pdf_files.append(pdf_filename)  # Add the filename to the list

    # Create a zip file containing all the PDF files
    zip_filename = "pdf_files.zip"
    with zipfile.ZipFile(zip_filename, 'w') as zipf:
        for pdf_file in pdf_files:
            zipf.write(pdf_file)

    # Provide a download button for the zip file
    with open(zip_filename, "rb") as file:
        zip_data = file.read()
    b64 = base64.b64encode(zip_data).decode()
    href = f'<a href="data:file/zip;base64,{b64}" download="{zip_filename}"><button>Click here to download the PDF files as a zip archive</button></a>'
    st.markdown(href, unsafe_allow_html=True)

    # Remove the individual PDF files and the zip file
    for pdf_file in pdf_files:
        os.remove(pdf_file)
    os.remove(zip_filename)

# Streamlit web app
def main():
    st.title('PDF Generator')
    uploaded_file = st.file_uploader("Upload CSV or Excel file", type=['csv', 'xlsx'])

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('csv') else pd.read_excel(uploaded_file)
        df = df.drop_duplicates()
        generate_pdf(df)
        st.success("PDF files generated successfully!")

if __name__ == '__main__':
    main()
