import streamlit as st
import pandas as pd
from fpdf import FPDF
import os
import zipfile
import base64

def generate_pdf(df):
    pdf_files = []  # List to store the names of the generated PDF files
    # Group by name and iterate over groups
    for EmployeeId, group in df.groupby('EmployeeId'):
        # Create a new PDF file for each user
        pdf = FPDF(orientation='L')  # Set PDF to landscape mode
        pdf.add_page()
        pdf.set_font("Arial", size=6)  # Reduce font size to 6

        # Add a title
        pdf.cell(200, 10, f"Details of SKID: {EmployeeId}", ln=True, align='C')
        pdf.ln(5)

        # Calculate the maximum length of text in each column excluding the 'name' column
        max_lengths = {column: max(group[column].astype(str).apply(len)) for column in group.columns if column !='EmployeeId'}

        # Define the default column width
        default_width = 12  # Increased default width to 20 for the first column

        # Add a table header
        pdf.set_fill_color(200, 220, 255)
        for column, max_length in max_lengths.items():
            column_width = max_length if max_length >= default_width else default_width
            pdf.cell(column_width * 2, 5, column[:10], 1, 0, 'C', 1)  # Set column width based on maximum text length or default width
        pdf.ln()

        # Add data to the table
        for _, row in group.iterrows():
            for column, max_length in max_lengths.items():
                cell_text = str(row[column]).replace('\n', ' ')  # Replace newline characters with spaces
                cell_text = cell_text.strip() if cell_text != 'nan' else ''  # Replace 'nan' values with blanks
                
                # Calculate the number of lines needed for the cell based on the maximum length in the column
                lines_needed = max_length // default_width + 1

                # Expand cell_text into multiple lines
                lines = [cell_text[i:i+default_width] for i in range(0, len(cell_text), default_width)]
                cell_text = "\n".join(lines)

                pdf.multi_cell(max_length * 2, 5, cell_text, 1, 'L')  # Print cell value with text wrapping

            pdf.ln()

        # Save the PDF file
        pdf_filename = f"SKID:{EmployeeId}_info.pdf"
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
        if os.path.exists(pdf_file):
            os.remove(pdf_file)
        else:
            st.warning(f"File not found: {pdf_file}")
    os.remove(zip_filename)

def main():
    st.title('Pdf Generator App')
    st.write('Upload a CSV or Excel file containing RM data to generate PDFs for each RM.')

    uploaded_file = st.file_uploader("Upload CSV or Excel file", type=['csv', 'xlsx'])

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('csv') else pd.read_excel(uploaded_file)
        df = df.applymap(str)
        df=df[df.apply(lambda x: x.str.match('^[\x00-\x7F]*$')).all(axis=1)]
        df = df.drop_duplicates()
        generate_pdf(df)
        st.success("PDF files generated successfully!")

if __name__ == '__main__':
    main()
