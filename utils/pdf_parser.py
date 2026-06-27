import PyPDF2
import docx
import streamlit as st


def parse_resume(uploaded_file):
    text = ""

    try:
        if uploaded_file.name.endswith('.pdf'):
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            for page in pdf_reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"

        elif uploaded_file.name.endswith('.docx'):
            doc = docx.Document(uploaded_file)
            for para in doc.paragraphs:
                text += para.text + "\n"

        else:
            st.error("❌ Unsupported file format. Please upload a PDF or DOCX file.")
            return ""

    except Exception as e:
        st.error(f"❌ Failed to read resume: {e}")
        return ""

    # Empty resume check — scanned PDF or corrupt file
    if not text.strip():
        st.warning("⚠️ No text could be extracted from your resume. This may be a scanned PDF image. Please upload a text-based PDF or DOCX file.")
        return ""

    return text.strip()