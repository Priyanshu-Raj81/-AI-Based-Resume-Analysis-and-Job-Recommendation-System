import streamlit as st
from utils.pdf_parser import parse_resume
from utils.nlp_extractor import extract_skills

def render_compare():
    st.title("📋 Resume Comparison Tool")
    st.write("Upload two different versions of your resume to compare extracted skills and completeness.")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Resume A")
        resume_a = st.file_uploader("Upload first resume", type=["pdf", "docx"], key="res_a")
        
    with col2:
        st.subheader("Resume B")
        resume_b = st.file_uploader("Upload second resume", type=["pdf", "docx"], key="res_b")
        
    if st.button("⚖️ Compare Resumes", type="primary", use_container_width=True):
        if resume_a and resume_b:
            with st.spinner("Extracting and comparing..."):
                text_a = parse_resume(resume_a)
                text_b = parse_resume(resume_b)
                
                skills_a = set(extract_skills(text_a))
                skills_b = set(extract_skills(text_b))
                
                common_skills = skills_a.intersection(skills_b)
                unique_a = skills_a - skills_b
                unique_b = skills_b - skills_a
                
            st.success("Comparison Complete!")
            
            res_col1, res_col2 = st.columns(2)
            with res_col1:
                st.info(f"**Resume A Total Skills:** {len(skills_a)}")
                st.write("**Unique to Resume A:**")
                for s in unique_a: st.write(f"✅ {s}")
                
            with res_col2:
                st.info(f"**Resume B Total Skills:** {len(skills_b)}")
                st.write("**Unique to Resume B:**")
                for s in unique_b: st.write(f"✅ {s}")
                
            st.markdown("---")
            st.write(f"**Shared Skills ({len(common_skills)}):** {', '.join(common_skills)}")
        else:
            st.warning("⚠️ Please upload both resumes to compare.")