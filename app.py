from flask import Flask, render_template, request, redirect, url_for, send_file, send_from_directory
import os
import matplotlib
matplotlib.use('Agg') # Fixes GUI threading warning
import matplotlib.pyplot as plt
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from groq import Groq
from dotenv import load_dotenv

# Local Imports
from utils.extractor import extract_text_from_file
from utils.analyzer import extract_skills, get_missing_skills, calculate_match, calculate_ml_match, get_job_links, run_full_ai_analysis
from db import init_db, create_user, verify_user

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

init_db()

# Global variables
extracted_text = ""
current_file = ""
current_user_name = "User"

# -------- AUTHENTICATION & LANDING --------
@app.route("/")
def home():
    return render_template("landing.html")



@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        full_name = request.form.get("full_name")
        email = request.form.get("email")
        ph_number = request.form.get("ph_number")
        password = request.form.get("password")
        
        success = create_user(full_name, email, ph_number, password)
        if success:
            return redirect(url_for("home"))
        return render_template("signup.html", error="Email already exists")
    
    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    global current_user_name
    if request.method == "GET":
        return render_template("login.html")
    email = request.form.get("email")
    password = request.form.get("password")
    user = verify_user(email, password)
    
    if user:
        current_user_name = user["full_name"]
        return redirect(url_for("dashboard"))
    return render_template("login.html", error="Invalid credentials")


@app.route("/logout")
def logout():
    global extracted_text, current_file, current_user_name
    extracted_text = ""
    current_file = ""
    current_user_name = "User"
    return redirect(url_for("home"))

# -------- DASHBOARD (Upload & Preview) --------
@app.route("/dashboard")
def dashboard():
    return render_template("index.html", name=current_user_name, current_file=current_file)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route("/upload", methods=["POST"])
def upload():
    global current_file
    
    if "resume" not in request.files:
        return "No file selected"
 
    file = request.files["resume"]
    if file.filename == "":
        return "Empty filename"

    filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(filepath)
    current_file = file.filename

    return redirect(url_for("dashboard"))

# -------- EXTRACT PAGE --------
@app.route("/extract_page", methods=["GET", "POST"])
def extract_page():
    global extracted_text, current_file

    if not current_file:
        # If accessing directly but no file, show error or blank
        return render_template("extract_page.html", text="", error="No file uploaded yet. Please upload a resume on the Dashboard.")

    filepath = os.path.join("uploads", current_file)
    extracted_text = extract_text_from_file(filepath)
    
    return render_template("extract_page.html", text=extracted_text, filename=current_file)

# -------- ANALYZE PAGE --------
@app.route("/analyze_page", methods=["GET"])
def analyze_page():
    if not extracted_text:
        return render_template("analyze_page.html", error="Please extract the text from your resume first via the Extract Text tab.")
    return render_template("analyze_page.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    global extracted_text ,resume_skills, missing_skills, score, matched_skills

    if not extracted_text:
        return redirect(url_for("analyze_page"))

    job_desc = request.form["job_desc"]
    
    # 1. Calculate Score mathematically
    score = calculate_ml_match(extracted_text, job_desc)

    # 2. Run consolidated AI Analysis
    from utils.analyzer import run_full_ai_analysis
    ai_result = run_full_ai_analysis(extracted_text, job_desc)
    
    # 3. Mathematically intersect the LLM extracted skills with Local DB to guarantee 100% accuracy
    import re
    from utils.analyzer import extract_skills
    
    # Combine AI extraction with strict Regex extraction so nothing is ever skipped
    job_skills_raw = ai_result.get("job_skills", []) + extract_skills(job_desc)
    resume_skills_raw = ai_result.get("resume_skills", []) + extract_skills(extracted_text)
    
    def normalize_skill(s):
        # Removes spaces, hyphens, slashes, and dots so "pl/sql" == "plsql" and "react.js" == "reactjs"
        return re.sub(r'[\s\-\/\.]', '', s.lower())

    # Create a normalized set of resume skills
    normalized_resume_skills = {normalize_skill(s) for s in resume_skills_raw if s.strip()}

    matched_skills = []
    missing_skills = []
    
    for skill in job_skills_raw:
        if not skill.strip():
            continue
        norm_skill = normalize_skill(skill)
        if norm_skill in normalized_resume_skills:
            matched_skills.append(skill.title())
        else:
            missing_skills.append(skill.title())
            
    # Remove duplicates that might arise from varying cases
    matched_skills = list(set(matched_skills))
    missing_skills = list(set(missing_skills))

    if not missing_skills:
        missing_skills = ["Everything matched ✅"]
        
    ai_suggestions = ai_result.get("suggestions", "")
    interview_questions = ai_result.get("interview_questions", "")

    # PIE CHART
    matched_pct = score
    missing_pct = max(0, 100 - score)

    labels = ["Matched", "Missing"]
    values = [matched_pct, missing_pct]

    plt.figure()
    plt.pie(values, labels=labels, autopct="%1.1f%%")
    plt.title("ML Skill Match Analysis")
    
    if not os.path.exists("static"):
       os.makedirs("static")
    chart_path = os.path.join("static", "chart.png")
    plt.savefig(chart_path)
    plt.close()

    job_links = get_job_links(matched_skills)
    
    resume_skills = matched_skills

    return render_template(
        "analysis.html",
        text=extracted_text,
        resume_skills=resume_skills,
        missing_skills=missing_skills,
        score=score,
        chart="chart.png",
        ai_suggestions=ai_suggestions,
        job_links=job_links,
        interview_questions=interview_questions
    )

@app.route("/download")
def download_report():
    global resume_skills, missing_skills, score
    file_path = "report.pdf"
    doc = SimpleDocTemplate(file_path)
    styles = getSampleStyleSheet()
    content = []
    content.append(Paragraph("Resume Analysis Report", styles["Title"]))
    content.append(Spacer(1, 10))
    content.append(Paragraph(f"ML Match Score: {score}%", styles["Normal"]))
    content.append(Spacer(1, 10))
    content.append(Paragraph("Matched Skills:", styles["Heading2"]))
    content.append(Paragraph(", ".join(resume_skills), styles["Normal"]))
    content.append(Spacer(1, 10))
    content.append(Paragraph("Missing Skills:", styles["Heading2"]))
    content.append(Paragraph(", ".join(missing_skills), styles["Normal"]))
    doc.build(content)
    return send_file(file_path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)