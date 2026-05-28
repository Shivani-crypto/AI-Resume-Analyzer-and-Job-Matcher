from groq import Groq
import os
from dotenv import load_dotenv
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


# Predefined skill list (you can expand later)
SKILLS_DB = [
    "python", "java", "c", "c++", "sql", "mysql", "postgresql", "mongodb", "nosql",
    "flask", "django", "fast api", "fastapi", "html", "css", "javascript", "typescript",
    "react", "node", "angular", "vue", "pandas", "numpy", "machine learning", "ml", "ai",
    "deep learning", "tensorflow", "keras", "pytorch", "api", "golang", "go", "rust",
    "docker", "kubernetes", "aws", "azure", "gcp", "git", "linux", "flutter", "dart",
    "swift", "kotlin", "android", "ios", "react native", "php", "ruby", "rails",
    "oracle", "pl/sql", "plsql", "soa", "osb", "bpel", "xml", "xsd", "xslt", "xpath",
    "xquery", "wsdl", "soap", "rest", "restful", "j2ee", "unix", "shell", "bpm", "owsm", "sap"
]


# -------- 1. EXTRACT SKILLS --------
def extract_skills(text):
    text = text.lower()
    found_skills = []

    for skill in SKILLS_DB:
        if re.search(r"\b" + re.escape(skill) + r"\b", text):
            found_skills.append(skill)

    return list(set(found_skills))


# -------- 2. MISSING SKILLS --------
def get_missing_skills(resume_skills, job_skills):
    missing = []

    for skill in job_skills:
        if skill not in resume_skills:
            missing.append(skill)

    return missing


# -------- 3. MATCH SCORE --------
def calculate_match(resume_skills, job_skills):
    if len(job_skills) == 0:
        return 0

    matched = 0

    for skill in job_skills:
        if skill in resume_skills:
            matched += 1

    score = (matched / len(job_skills)) * 100
    return round(score, 2)


# -------- 4. ML MATCH SCORE (TF-IDF Cosine Similarity) --------
def calculate_ml_match(resume_text, job_description):
    if not resume_text.strip() or not job_description.strip():
        return 0

    vectorizer = TfidfVectorizer(stop_words='english')
    vectors = vectorizer.fit_transform([resume_text, job_description])
    
    similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
    return round(similarity * 100, 2)


import json

def run_full_ai_analysis(resume_text, job_desc):
    prompt = f"""
    You are an expert AI Technical Recruiter. Analyze the following Resume against the Job Description.
    Identify ALL technical skills, tools, programming languages, and frameworks.
    
    1. Extract all technical skills required by the Job Description. (job_skills)
    2. Extract all technical skills possessed by the candidate from the Resume. (resume_skills)
    3. Generate 5 short, actionable suggestions on how the candidate can improve their resume for this job.
    4. Generate 5 simple interview questions based on the required skills.

    Return EXACTLY a JSON object with the following keys. 
    Format the suggestions and interview_questions strictly as HTML strings (use <ul>, <ol>, <li>, <strong>).
    Do NOT use Markdown.

    {{
      "job_skills": ["skill1", "skill2"],
      "resume_skills": ["skill1", "skill3"],
      "suggestions": "<ul><li>suggestion 1</li></ul>",
      "interview_questions": "<ol><li>question 1</li></ol>"
    }}

    Job Description:
    {job_desc[:3000]}

    Resume:
    {resume_text[:3000]}
    """

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that outputs only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        result_text = response.choices[0].message.content.strip()
        
        # Clean up possible markdown wrappers from the LLM response
        if result_text.startswith("```json"):
            result_text = result_text[7:]
        elif result_text.startswith("```"):
            result_text = result_text[3:]
            
        if result_text.endswith("```"):
            result_text = result_text[:-3]
            
        return json.loads(result_text.strip())
    except Exception as e:
        print("AI Analysis Error:", e)
        # Fallback to local DB extraction if the AI fails or gets rate limited
        return {
            "job_skills": extract_skills(job_desc),
            "resume_skills": extract_skills(resume_text),
            "suggestions": "<p><em>Warning: AI Suggestions unavailable due to API rate limits. Local database used for keyword matching.</em></p>",
            "interview_questions": "<p><em>Warning: AI Questions unavailable.</em></p>"
        }

def get_job_links(skills):
    query = "+".join(skills)

    return {
        "LinkedIn": f"https://www.linkedin.com/jobs/search/?keywords={query}",
        "Indeed": f"https://www.indeed.com/jobs?q={query}",
        "Naukri": f"https://www.naukri.com/{query}-jobs"
    }


