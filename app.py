import io
from pathlib import Path

import pandas as pd
import streamlit as st

from database import create_database, save_result
from resume_processor import clean_text, extract_text_from_pdf
from screening import ROLE_REQUIRED_SKILLS, screen_resume

st.set_page_config(page_title="AI CareerMatch", page_icon="🤖", layout="wide")
create_database()

# ---------------- STYLE ----------------
st.markdown("""
<style>
.stApp{background:radial-gradient(circle at 10% 0%,rgba(58,91,170,.30),transparent 28%),radial-gradient(circle at 90% 5%,rgba(124,62,170,.28),transparent 30%),#050d1b;color:#eaf1ff}
[data-testid="stHeader"]{background:transparent}.block-container{max-width:1320px;padding-top:1.5rem;padding-bottom:3rem}
h1,h2,h3,h4{color:#fff!important}.hero{padding:30px;border:1px solid #31547f;border-radius:24px;background:linear-gradient(135deg,rgba(17,42,78,.96),rgba(42,24,67,.96));box-shadow:0 15px 45px rgba(0,0,0,.28);margin-bottom:24px}.hero h1{font-size:42px;margin:0}.hero p{color:#b8c9e5;margin:8px 0 0;font-size:16px}.card{background:rgba(10,26,49,.84);border:1px solid #29476e;border-radius:17px;padding:18px;margin:8px 0}.job-card{background:linear-gradient(135deg,rgba(15,39,72,.95),rgba(31,25,59,.95));border:1px solid #3b5e8f;border-radius:18px;padding:18px;margin:8px 0}.job-title{font-size:21px;font-weight:700;color:#fff}.job-score{font-size:25px;font-weight:800;color:#a9c8ff}.pill{display:inline-block;padding:5px 10px;margin:3px;border:1px solid #416998;border-radius:18px;background:#0b1d37;color:#dce9ff;font-size:12px}.good{color:#7ee2a8}.warn{color:#ffd27d}.muted{color:#8fa7ca}.stButton>button,.stDownloadButton>button{background:#315fbd!important;color:#fff!important;border:1px solid #527ed5!important;border-radius:10px!important}.stButton>button:hover{background:#3b6fd6!important}.stTextInput input,.stSelectbox>div,.stMultiSelect>div{background:#0b1b33!important;color:#fff!important}.stFileUploader{background:#0b1b33!important;border:1px solid #365b88!important;border-radius:16px!important}.stProgress>div>div>div{background:#527ed5!important}[data-testid="stMetric"]{background:rgba(10,27,51,.9)!important;border:1px solid #29476e!important;border-radius:15px!important;padding:14px!important}[data-testid="stMetricLabel"]{color:#91a9cf!important}[data-testid="stMetricValue"]{color:#fff!important}.footer{text-align:center;color:#7187a8;margin-top:35px;font-size:13px}
</style>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
st.sidebar.markdown("## 🤖 AI Career Analyzer")
st.sidebar.markdown("**Features**")
for item in ["Resume screening", "Job-role recommendation", "Skill-gap analysis", "Candidate ranking", "Career roadmap", "Interview preparation", "Resume improvement"]:
    st.sidebar.write("✓ " + item)
st.sidebar.markdown("---")
st.sidebar.caption("NLP-based intelligent scoring • Streamlit • Python")

# ---------------- HERO ----------------
st.markdown("""
<div class="hero">
<h1>🤖 AI CareerMatch — Intelligent Resume Screening & Job Recommendation</h1>
<p>Analyze resumes, rank candidates, discover suitable job roles, identify skill gaps and generate a personalized career roadmap.</p>
</div>
""", unsafe_allow_html=True)

# ---------------- UPLOAD ----------------
st.header("📄 Upload Resumes")
uploaded_files = st.file_uploader("Upload one or more PDF resumes", type=["pdf"], accept_multiple_files=True)

if uploaded_files:
    st.success(f"{len(uploaded_files)} resume(s) ready for analysis.")
    if st.button("🚀 Analyze Resumes & Recommend Jobs", use_container_width=True):
        results=[]; progress=st.progress(0); folder=Path("uploads"); folder.mkdir(exist_ok=True)
        for i, file in enumerate(uploaded_files,1):
            try:
                path=folder/file.name; path.write_bytes(file.getbuffer())
                text=extract_text_from_pdf(str(path))
                if not text.strip():
                    st.warning(f"No readable text found in {file.name}."); continue
                result=screen_resume(text, clean_text(text)); result["filename"]=file.name; results.append(result)
                try: save_result(result)
                except Exception: pass
            except Exception as e:
                st.error(f"Could not process {file.name}: {e}")
            progress.progress(i/len(uploaded_files))
        if results:
            st.session_state.results=results
            st.success("Analysis completed — job recommendations are now available below.")

results=sorted(st.session_state.get("results",[]),key=lambda x:x.get("overall_score",0),reverse=True)

if results:
    st.session_state.results=results
    total=len(results); avg=sum(x["overall_score"] for x in results)/total
    shortlisted=sum(x["status"]=="Shortlisted" for x in results)
    consider=sum(x["status"]=="Consider" for x in results)
    top=results[0]["overall_score"]

    st.header("📊 Screening Dashboard")
    c=st.columns(6)
    c[0].metric("📄 Resumes",total); c[1].metric("📊 Average",f"{avg:.1f}%"); c[2].metric("🏆 Shortlisted",shortlisted); c[3].metric("🟡 Consider",consider); c[4].metric("⭐ Top Score",f"{top:.1f}%"); c[5].metric("💼 Roles",len(ROLE_REQUIRED_SKILLS))

    # Ranking
    st.header("🏆 Candidate Ranking")
    rows=[]
    for rank,x in enumerate(results,1):
        rows.append({"Rank":rank,"Candidate":x.get("candidate_name"),"Best Job Role":x.get("recommended_role"),"AI Score":x.get("overall_score"),"Experience":f"{x.get('experience_years',0):g} yrs","Skills":len(x.get("skills",[])),"Status":x.get("status")})
    ranking_df=pd.DataFrame(rows)
    st.dataframe(ranking_df,use_container_width=True,hide_index=True)

    # Job recommendation leaderboard
    st.header("💼 Job Recommendations")
    st.caption("The system does not just choose one role. It ranks several roles based on resume skills and role similarity.")
    job_source=results[0]
    jobs=job_source.get("job_recommendations",[])[:5]
    for j in jobs:
        matched=j["matched_skills"][:6]; missing=j["missing_skills"][:4]
        st.markdown(f"""
        <div class="job-card">
        <div class="job-title">💼 {j['role']} <span class="job-score">{j['fit_score']:.1f}% fit</span></div>
        <div class="muted">{j['description']}</div><br>
        <b>Matched skills:</b> {' '.join(f'<span class="pill">{s}</span>' for s in matched) if matched else '<span class="warn">No direct matches detected</span>'}<br>
        <b>Skills to improve:</b> {' '.join(f'<span class="pill">{s}</span>' for s in missing) if missing else '<span class="good">Strong coverage</span>'}
        </div>
        """,unsafe_allow_html=True)

    # Analytics
    st.header("📈 Analytics")
    a,b=st.columns(2)
    with a:
        score_df=pd.DataFrame({"Candidate":[x.get("candidate_name",f"Candidate {i+1}") for i,x in enumerate(results)],"Score":[x["overall_score"] for x in results]}).set_index("Candidate")
        st.bar_chart(score_df)
    with b:
        role_count={}
        for x in results: role_count[x["recommended_role"]]=role_count.get(x["recommended_role"],0)+1
        st.bar_chart(pd.DataFrame({"Candidates":role_count}))

    # Individual analysis
    st.header("🔎 Candidate Intelligence")
    names=[x.get("candidate_name",f"Candidate {i+1}") for i,x in enumerate(results)]
    chosen=st.selectbox("Choose a candidate",names)
    item=next(x for x in results if x.get("candidate_name")==chosen)

    tabs=st.tabs(["🎯 Job Fit","🧠 Skills","📈 Score","🛠️ Resume Improvement","🎤 Interview Prep","🗺️ Career Roadmap"])
    with tabs[0]:
        st.subheader("Best-fit jobs")
        for j in item.get("job_recommendations",[])[:7]:
            st.write(f"**{j['role']} — {j['fit_score']:.1f}% fit**")
            st.progress(min(100,int(j['fit_score'])))
            st.caption(j["description"])
        st.info(f"Recommended starting role: {item['recommended_role']}")

    with tabs[1]:
        st.subheader("Detected skills")
        skills=item.get("skills",[])
        st.markdown(" ".join(f'<span class="pill">{s}</span>' for s in skills) if skills else "No skills detected",unsafe_allow_html=True)
        st.subheader("Skill gap for recommended role")
        missing=item.get("missing_role_skills",[])
        if missing:
            st.warning("Priority skills: " + ", ".join(missing))
        else: st.success("Excellent coverage for the recommended role.")

    with tabs[2]:
        st.subheader("Explainable AI score")
        parts=[("Role Match",item["role_match_score"]),("Skills",item["skill_score"]),("Resume Quality",item["quality_score"]),("Experience",item["experience_score"]),("Resume Completeness",item["resume_completeness"])]
        for label,val in parts:
            st.write(f"**{label}: {val:.1f}%**"); st.progress(min(100,max(0,int(val))))
        st.metric("Final AI Screening Score",f"{item['overall_score']:.1f}%")

    with tabs[3]:
        st.subheader("How to improve this resume")
        for s in item.get("suggestions",[]): st.info("💡 "+s)
        st.subheader("Recommended next skills")
        next_skills=[]
        for j in item.get("job_recommendations",[])[:3]: next_skills += j.get("next_skills",[])
        st.markdown(" ".join(f'<span class="pill">{s}</span>' for s in dict.fromkeys(next_skills)),unsafe_allow_html=True)

    with tabs[4]:
        st.subheader("Interview preparation")
        role=item["recommended_role"]
        questions={
            "Python Developer":["Explain a Python project you built.","How do you handle exceptions in Python?","Explain REST APIs and how you used one.","How did you use Git in a project?"],
            "Data Analyst":["Explain a data-analysis project.","How do GROUP BY and HAVING differ in SQL?","How would you clean missing data?","Which dashboard would you build for a business problem?"],
            "Machine Learning Engineer":["Explain one ML project end-to-end.","Why do we split data into training and testing sets?","How do you evaluate a classification model?","How would you deploy an ML model?"],
            "Web Developer":["Explain the architecture of one web project.","What is the difference between frontend and backend?","How does an API connect the two?","How do you test a web application?"],
        }
        qs=questions.get(role,[f"Explain your strongest {role} project.","Which technical skill are you strongest in?","Describe a difficult bug or problem you solved.","What would you improve in your projects?"])
        for i,q in enumerate(qs,1): st.write(f"**{i}. {q}**")

    with tabs[5]:
        st.subheader("Personalized career roadmap")
        top_role=item["recommended_role"]
        st.write(f"**Current best fit:** {top_role}")
        roadmap=item.get("job_recommendations",[])[0].get("next_skills",[])
        for i,skill in enumerate(roadmap,1):
            st.write(f"**Step {i}:** Learn/practice **{skill}**")
        st.write("**Next:** Build a project using the new skill → add measurable results to the resume → apply for matching roles.")

    # All role scores
    with st.expander("📌 View all role matching scores"):
        rs=item.get("role_scores",{})
        st.dataframe(pd.DataFrame({"Job Role":list(rs.keys()),"Text Match Score":list(rs.values())}).sort_values("Text Match Score",ascending=False),use_container_width=True,hide_index=True)

    # Exports
    st.header("📥 Export")
    e1,e2,e3=st.columns(3)
    with e1: st.download_button("📊 Download Ranking CSV",ranking_df.to_csv(index=False),"candidate_ranking.csv","text/csv",use_container_width=True)
    with e2:
        job_df=pd.DataFrame([{"Candidate":item["candidate_name"],"Job Role":j["role"],"Fit Score":j["fit_score"],"Missing Skills":", ".join(j["missing_skills"])} for j in item.get("job_recommendations",[])])
        st.download_button("💼 Download Job Matches",job_df.to_csv(index=False),"job_recommendations.csv","text/csv",use_container_width=True)
    with e3:
        report=io.StringIO(); report.write("AI RESUME CAREER ANALYSIS REPORT\n"+"="*55+"\n\n")
        report.write(f"Candidate: {item['candidate_name']}\nBest role: {item['recommended_role']}\nAI score: {item['overall_score']:.1f}%\n\nTOP JOB RECOMMENDATIONS\n")
        for j in item.get("job_recommendations",[])[:7]: report.write(f"- {j['role']}: {j['fit_score']:.1f}% fit\n")
        report.write("\nSKILL GAPS\n"+", ".join(item.get("missing_role_skills",[])))
        st.download_button("📄 Download Analysis Report",report.getvalue(),"career_analysis_report.txt","text/plain",use_container_width=True)

    if st.button("🗑️ Clear Results",use_container_width=True):
        st.session_state.pop("results",None); st.rerun()

st.markdown('<div class="footer">AI CareerMatch • Resume Screening • Job Recommendation • Career Guidance • NLP</div>',unsafe_allow_html=True)
