# AI-Based Resume Screening System

A BTech 2nd-year level project that uses NLP and machine learning to automatically analyze PDF resumes.

## Main Features

- PDF-only resume upload
- Automatic resume text extraction
- NLP text cleaning
- Skill extraction
- TF-IDF and cosine similarity
- Automatic recommended-role prediction
- AI screening score
- Candidate ranking
- Resume quality analysis
- Skill-gap/improvement suggestions
- SQLite screening history
- Downloadable ranking table
- Streamlit dashboard

## How the AI works

The user only uploads PDF resumes. The system does not require a job-description box.

1. Extract text from each PDF.
2. Clean the text using NLP.
3. Detect recognized skills.
4. Compare the resume with built-in role profiles using TF-IDF and cosine similarity.
5. Select the best matching role.
6. Combine role similarity, skill coverage, resume quality, and experience into an overall score.
7. Rank all uploaded candidates.
8. Store screening history in SQLite.

## Project Structure

AI_Resume_Screening/
- app.py
- resume_processor.py
- nlp_processor.py
- screening.py
- database.py
- requirements.txt
- data/skills.csv
- uploads/
- database/
- reports/

## Installation

Open CMD in this folder and activate the environment:

```cmd
venv\Scripts\activate
```

Install packages:

```cmd
python -m pip install -r requirements.txt
```

Download NLTK stopwords:

```cmd
python -c "import nltk; nltk.download('stopwords')"
```

Run:

```cmd
python -m streamlit run app.py
```

Then open the Streamlit URL shown in CMD, normally:

```text
http://localhost:8501
```

## Note

This is an academic screening prototype. Its score is an automated indication, not a hiring decision.
