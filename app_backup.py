import streamlit as st
from pathlib import Path
import pandas as pd

from resume_processor import extract_resume_text
from nlp_processor import clean_text, extract_skills
from screening import screen_resume
from database import create_database, save_candidate, get_candidates


st.set_page_config(
    page_title="AI Resume Screening",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed",
)

create_database()

# ---------- Styling ----------
st.markdown("""
<style>
    .main-title {
        font-size: 2.35rem;
        font-weight: 750;
        margin-bottom: 0.2rem;
    }
    .subtitle {
        color: #667085;
        font-size: 1rem;
        margin-bottom: 1.4rem;
    }
    .upload-box {
        border: 1px dashed #98A2B3;
        border-radius: 14px;
        padding: 22px;
        background: #F8FAFC;
    }
    .section-title {
        font-size: 1.25rem;
        font-weight: 700;
        margin-top: 1rem;
    }
    .score {
        font-size: 2.1rem;
        font-weight: 800;
    }
    .small-muted {
        color: #667085;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">📄 AI-Based Resume Screening System</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Upload PDF resumes and let the system automatically analyze skills, resume quality, role suitability, and ranking.</div>',
    unsafe_allow_html=True
)

# ---------- Upload ----------
st.markdown('<div class="section-title">Upload PDF Resumes</div>', unsafe_allow_html=True)
uploaded_files = st.file_uploader(
    "Select one or more PDF resumes",
    type=["pdf"],
    accept_multiple_files=True,
    help="Only PDF resumes are supported."
)

if uploaded_files:
    st.caption(f"{len(uploaded_files)} PDF resume(s) selected.")

if st.button("🚀 Analyze Resumes", type="primary", use_container_width=True):
    if not uploaded_files:
        st.warning("Please upload at least one PDF resume.")
        st.stop()

    results = []

    with st.spinner("Analyzing resumes with NLP and machine-learning models..."):
        for uploaded_file in uploaded_files:
            path = Path("uploads") / uploaded_file.name
            path.write_bytes(uploaded_file.getbuffer())

            try:
                text = extract_resume_text(str(path))
                cleaned = clean_text(text)
                result = screen_resume(text, cleaned)

                result["resume_name"] = uploaded_file.name
                results.append(result)

            except Exception as exc:
                st.error(f"Could not process {uploaded_file.name}: {exc}")

    if not results:
        st.error("No resume could be processed.")
        st.stop()

    ranked = sorted(results, key=lambda x: x["overall_score"], reverse=True)

    for rank, item in enumerate(ranked, start=1):
        item["rank"] = rank
        save_candidate(item, rank)

    st.session_state["results"] = ranked

# ---------- Results ----------
if "results" in st.session_state:
    ranked = st.session_state["results"]

    st.divider()
    st.markdown("## 📊 Screening Summary")

    avg_score = sum(x["overall_score"] for x in ranked) / len(ranked)
    shortlisted = sum(x["status"] == "Shortlisted" for x in ranked)
    top_role = ranked[0]["recommended_role"]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Resumes", len(ranked))
    c2.metric("Average Score", f"{avg_score:.1f}%")
    c3.metric("Shortlisted", shortlisted)
    c4.metric("Top Candidate", ranked[0]["resume_name"])

    st.markdown("## 🏆 Candidate Ranking")

    table_rows = []
    for x in ranked:
        table_rows.append({
            "Rank": x["rank"],
            "Resume": x["resume_name"],
            "AI Score": f"{x['overall_score']:.1f}%",
            "Recommended Role": x["recommended_role"],
            "Status": x["status"],
            "Skills Found": len(x["skills"]),
            "Experience": f"{x['experience_years']:.1f} yrs",
        })

    df = pd.DataFrame(table_rows)
    st.dataframe(df, use_container_width=True, hide_index=True)

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "📥 Download Ranking Table",
        data=csv,
        file_name="resume_screening_results.csv",
        mime="text/csv",
    )

    st.markdown("## 🔎 Detailed Candidate Analysis")

    for x in ranked:
        with st.expander(
            f"#{x['rank']}  {x['resume_name']}  —  {x['overall_score']:.1f}%  —  {x['status']}"
        ):
            a, b, c = st.columns(3)
            a.metric("AI Screening Score", f"{x['overall_score']:.1f}%")
            b.metric("Best Role Match", x["recommended_role"])
            c.metric("Resume Quality", f"{x['quality_score']:.1f}%")

            st.markdown("### 🧠 Score Breakdown")
            breakdown = pd.DataFrame({
                "Component": ["Role Match", "Skill Coverage", "Resume Quality", "Experience"],
                "Score": [
                    x["role_match_score"],
                    x["skill_score"],
                    x["quality_score"],
                    x["experience_score"],
                ],
            })
            st.dataframe(breakdown, use_container_width=True, hide_index=True)

            left, right = st.columns(2)

            with left:
                st.markdown("### ✅ Detected Skills")
                if x["skills"]:
                    st.write(", ".join(x["skills"]))
                else:
                    st.info("No recognized technical skills were detected.")

            with right:
                st.markdown("### ⚠️ Improvement Suggestions")
                for suggestion in x["suggestions"]:
                    st.write(f"• {suggestion}")

            st.markdown("### 📌 Resume Information")
            info = pd.DataFrame({
                "Field": ["Name", "Email", "Phone", "Education", "Experience"],
                "Detected Value": [
                    x["candidate_name"],
                    x["email"],
                    x["phone"],
                    x["education"],
                    f"{x['experience_years']:.1f} years",
                ],
            })
            st.dataframe(info, use_container_width=True, hide_index=True)

    st.markdown("## 🗂️ Screening History")

    history = get_candidates()
    if history:
        hist_df = pd.DataFrame(history)
        st.dataframe(hist_df, use_container_width=True, hide_index=True)

st.divider()
st.caption("AI Resume Screening System • BTech Project • PDF-only input")
