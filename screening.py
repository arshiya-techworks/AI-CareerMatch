import re
import math
from collections import Counter
from pathlib import Path

ROLE_PROFILES = {
    "Python Developer": "python django flask fastapi sql mysql mongodb git github rest api pandas numpy programming algorithms",
    "Data Analyst": "python sql pandas numpy excel data analysis statistics power bi tableau visualization",
    "Machine Learning Engineer": "python machine learning deep learning tensorflow pytorch pandas numpy scikit-learn statistics algorithms",
    "Web Developer": "html css javascript react django flask python frontend backend web development git github",
    "Software Developer": "python java c c++ sql git github data structures algorithms object oriented programming software development",
    "Data Scientist": "python pandas numpy statistics machine learning scikit-learn tensorflow sql data visualization analytics",
    "AI Engineer": "python artificial intelligence machine learning deep learning pytorch tensorflow nlp computer vision transformers",
    "Backend Developer": "python java node js django flask fastapi api sql mysql mongodb backend git docker",
    "Frontend Developer": "html css javascript react angular typescript ui ux frontend responsive web git",
    "Database Developer": "sql mysql postgresql oracle database plsql queries normalization stored procedures",
    "DevOps Engineer": "linux git docker kubernetes aws azure ci cd jenkins python cloud devops",
    "Cloud Engineer": "aws azure cloud linux docker kubernetes networking python devops",
    "Cybersecurity Analyst": "cybersecurity network security linux python ethical hacking vulnerability security siem",
    "Business Analyst": "business analysis requirements sql excel power bi tableau communication documentation",
    "QA / Test Engineer": "testing software testing selenium automation python java test cases quality assurance debugging",
}

ROLE_REQUIRED_SKILLS = {
    "Python Developer": ["python", "django", "flask", "fastapi", "sql", "git", "github", "rest api", "pandas", "numpy"],
    "Data Analyst": ["python", "sql", "pandas", "numpy", "excel", "data analysis", "statistics", "power bi", "tableau"],
    "Machine Learning Engineer": ["python", "machine learning", "deep learning", "tensorflow", "pytorch", "pandas", "numpy", "scikit-learn", "statistics"],
    "Web Developer": ["html", "css", "javascript", "react", "django", "flask", "python", "frontend", "backend", "git"],
    "Software Developer": ["python", "java", "c", "c++", "sql", "git", "github", "data structures", "algorithms", "object oriented programming"],
    "Data Scientist": ["python", "pandas", "numpy", "statistics", "machine learning", "scikit-learn", "sql", "data visualization"],
    "AI Engineer": ["python", "artificial intelligence", "machine learning", "deep learning", "pytorch", "tensorflow", "nlp"],
    "Backend Developer": ["python", "java", "django", "flask", "fastapi", "sql", "mongodb", "rest api", "docker"],
    "Frontend Developer": ["html", "css", "javascript", "react", "typescript", "frontend", "ui", "responsive web"],
    "Database Developer": ["sql", "mysql", "postgresql", "oracle", "database", "plsql", "queries"],
    "DevOps Engineer": ["linux", "git", "docker", "kubernetes", "aws", "ci/cd", "jenkins", "python"],
    "Cloud Engineer": ["aws", "azure", "cloud", "linux", "docker", "kubernetes", "networking", "python"],
    "Cybersecurity Analyst": ["cybersecurity", "network security", "linux", "python", "ethical hacking", "vulnerability", "security"],
    "Business Analyst": ["business analysis", "requirements", "sql", "excel", "power bi", "tableau", "communication"],
    "QA / Test Engineer": ["testing", "software testing", "selenium", "automation", "python", "java", "test cases", "debugging"],
}

ROLE_DESCRIPTIONS = {
    "Python Developer": "Builds applications, APIs and automation using Python and backend frameworks.",
    "Data Analyst": "Turns business data into insights using SQL, spreadsheets, Python and dashboards.",
    "Machine Learning Engineer": "Develops and integrates machine-learning models into software systems.",
    "Web Developer": "Creates full web applications across frontend and backend technologies.",
    "Software Developer": "Designs, codes, tests and maintains general-purpose software applications.",
    "Data Scientist": "Uses statistics, programming and machine learning to discover patterns in data.",
    "AI Engineer": "Builds AI-powered applications using machine learning, NLP and deep learning.",
    "Backend Developer": "Develops APIs, databases and server-side application logic.",
    "Frontend Developer": "Builds responsive user interfaces and browser-based experiences.",
    "Database Developer": "Designs databases, queries, procedures and data-management solutions.",
    "DevOps Engineer": "Automates software delivery, deployment, infrastructure and CI/CD workflows.",
    "Cloud Engineer": "Designs and manages applications and infrastructure on cloud platforms.",
    "Cybersecurity Analyst": "Monitors systems, identifies security risks and supports defensive security operations.",
    "Business Analyst": "Connects business needs with technical solutions through requirements and analysis.",
    "QA / Test Engineer": "Tests software, finds defects and improves product reliability through manual and automated testing.",
}

ROLE_NEXT_SKILLS = {
    "Python Developer": ["Docker", "REST API", "AWS", "FastAPI"],
    "Data Analyst": ["Power BI", "Tableau", "Advanced SQL", "Statistics"],
    "Machine Learning Engineer": ["MLOps", "Docker", "Cloud", "Deep Learning"],
    "Web Developer": ["React", "TypeScript", "REST API", "Docker"],
    "Software Developer": ["System Design", "Git", "Testing", "Cloud"],
    "Data Scientist": ["Deep Learning", "SQL", "MLOps", "Cloud"],
    "AI Engineer": ["LLM", "RAG", "MLOps", "Cloud"],
    "Backend Developer": ["Docker", "Kubernetes", "Cloud", "System Design"],
    "Frontend Developer": ["TypeScript", "Next.js", "Testing", "UI/UX"],
    "Database Developer": ["Cloud Databases", "ETL", "Performance Tuning", "Python"],
    "DevOps Engineer": ["Terraform", "AWS", "Kubernetes", "Monitoring"],
    "Cloud Engineer": ["Terraform", "Kubernetes", "Security", "DevOps"],
    "Cybersecurity Analyst": ["SIEM", "Incident Response", "Cloud Security", "Threat Detection"],
    "Business Analyst": ["Power BI", "SQL", "Agile", "Process Modeling"],
    "QA / Test Engineer": ["Selenium", "API Testing", "CI/CD", "Automation"],
}


def tokenize(text):
    return re.findall(r"[a-zA-Z0-9+#./-]+", text.lower())


def cosine_similarity(text1, text2):
    words1, words2 = tokenize(text1), tokenize(text2)
    if not words1 or not words2:
        return 0.0
    count1, count2 = Counter(words1), Counter(words2)
    all_words = set(count1) | set(count2)
    total1, total2 = len(words1), len(words2)
    vector1 = {w: count1[w] / total1 for w in all_words}
    vector2 = {w: count2[w] / total2 for w in all_words}
    dot = sum(vector1[w] * vector2[w] for w in all_words)
    mag1 = math.sqrt(sum(v * v for v in vector1.values()))
    mag2 = math.sqrt(sum(v * v for v in vector2.values()))
    if not mag1 or not mag2:
        return 0.0
    return (dot / (mag1 * mag2)) * 100


def estimate_experience(text):
    pattern = r"(\d+(?:\.\d+)?)\s*\+?\s*years?\s*(?:of)?\s*(?:experience|work)"
    return max((float(v) for v in re.findall(pattern, text.lower())), default=0.0)


def detect_contact(text):
    email = re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", text)
    digits = re.sub(r"\D", "", text)
    phone = re.search(r"(?:91)?[6-9]\d{9}", digits)
    return (email.group(0) if email else "Not detected", phone.group(0) if phone else "Not detected")


def detect_name(text):
    lines = [x.strip() for x in text.splitlines() if x.strip()]
    for line in lines[:8]:
        if 1 <= len(line.split()) <= 5 and not re.search(r"[@\d]", line):
            return line
    return "Not detected"


def detect_education(text):
    terms = ["b.tech", "btech", "b.e", "bachelor", "m.tech", "mtech", "master", "b.sc", "bca", "mca", "degree"]
    lower = text.lower()
    found = [term for term in terms if term in lower]
    return ", ".join(dict.fromkeys(found)) if found else "Not detected"


def calculate_quality_score(text, skills, email, phone, education):
    words = len(text.split())
    score = 30 if words >= 150 else 20 if words >= 80 else 10
    score += min(30, len(skills) * 3)
    score += 15 if email != "Not detected" else 0
    score += 10 if phone != "Not detected" else 0
    score += 15 if education != "Not detected" else 0
    return min(score, 100)


def _norm(value):
    return re.sub(r"\s+", " ", str(value).lower().strip())


def get_role_skill_analysis(role, skills):
    required = ROLE_REQUIRED_SKILLS.get(role, [])
    detected = {_norm(x) for x in skills}
    matched = [x for x in required if _norm(x) in detected]
    missing = [x for x in required if _norm(x) not in detected]
    return required, matched, missing


def recommend_jobs(skills, role_scores, experience_years):
    """Return ranked career-role recommendations using detected skills + role similarity."""
    detected = {_norm(x) for x in skills}
    recommendations = []
    for role, required in ROLE_REQUIRED_SKILLS.items():
        matched = [s for s in required if _norm(s) in detected]
        missing = [s for s in required if _norm(s) not in detected]
        skill_fit = (len(matched) / len(required) * 100) if required else 0
        text_fit = role_scores.get(role, 0)
        # Blend semantic/text similarity and explicit skill coverage.
        fit = round(min(100, text_fit * 0.55 + skill_fit * 0.45), 2)
        if experience_years >= 1:
            experience_bonus = min(5, experience_years)
            fit = round(min(100, fit + experience_bonus), 2)
        recommendations.append({
            "role": role,
            "fit_score": fit,
            "matched_skills": matched,
            "missing_skills": missing,
            "description": ROLE_DESCRIPTIONS.get(role, ""),
            "next_skills": ROLE_NEXT_SKILLS.get(role, []),
        })
    return sorted(recommendations, key=lambda x: x["fit_score"], reverse=True)


def screen_resume(original_text, cleaned_text):
    import pandas as pd
    from nlp_processor import extract_skills

    skills_path = Path("data") / "skills.csv"
    skills_df = pd.read_csv(skills_path)
    skills_list = skills_df["skill"].dropna().tolist()
    skills = extract_skills(original_text, skills_list)

    role_scores = {role: cosine_similarity(cleaned_text, profile) for role, profile in ROLE_PROFILES.items()}
    recommended_role = max(role_scores, key=role_scores.get)
    role_match_score = role_scores[recommended_role]
    skill_score = min(100, len(skills) * 8)
    experience_years = estimate_experience(original_text)
    experience_score = min(100, experience_years * 20) if experience_years > 0 else 35
    email, phone = detect_contact(original_text)
    education = detect_education(original_text)
    candidate_name = detect_name(original_text)
    quality_score = calculate_quality_score(original_text, skills, email, phone, education)

    overall_score = round(min(
        role_match_score * 0.45 + skill_score * 0.25 + quality_score * 0.20 + experience_score * 0.10,
        100,
    ), 2)
    status = "Shortlisted" if overall_score >= 75 else "Consider" if overall_score >= 55 else "Needs Review"

    _, matched_role_skills, missing_role_skills = get_role_skill_analysis(recommended_role, skills)
    job_recommendations = recommend_jobs(skills, role_scores, experience_years)

    suggestions = []
    if len(skills) < 6:
        suggestions.append("Add more relevant technical skills.")
    if email == "Not detected":
        suggestions.append("Add a professional email address.")
    if phone == "Not detected":
        suggestions.append("Add a contact phone number.")
    if education == "Not detected":
        suggestions.append("Clearly mention your education.")
    if experience_years == 0:
        suggestions.append("Add projects, internships, certifications or practical experience.")
    if len(original_text.split()) < 100:
        suggestions.append("Add detailed project, achievement and responsibility descriptions.")
    if missing_role_skills:
        suggestions.append("For the top role, consider developing: " + ", ".join(missing_role_skills[:5]) + ".")
    if not suggestions:
        suggestions.append("Resume has good basic coverage. Focus on measurable achievements and role-specific keywords.")

    completeness = round(min(100, (
        (20 if candidate_name != "Not detected" else 0)
        + (15 if email != "Not detected" else 0)
        + (10 if phone != "Not detected" else 0)
        + (15 if education != "Not detected" else 0)
        + (20 if skills else 0)
        + (10 if experience_years > 0 else 0)
        + (10 if len(original_text.split()) >= 150 else 5 if len(original_text.split()) >= 80 else 0)
    )), 2)

    return {
        "candidate_name": candidate_name,
        "email": email,
        "phone": phone,
        "education": education,
        "experience_years": experience_years,
        "skills": skills,
        "recommended_role": recommended_role,
        "role_scores": {k: round(v, 2) for k, v in role_scores.items()},
        "role_match_score": round(role_match_score, 2),
        "skill_score": round(skill_score, 2),
        "quality_score": round(quality_score, 2),
        "experience_score": round(experience_score, 2),
        "overall_score": overall_score,
        "status": status,
        "resume_completeness": completeness,
        "matched_role_skills": matched_role_skills,
        "missing_role_skills": missing_role_skills,
        "suggestions": suggestions,
        "job_recommendations": job_recommendations,
    }
