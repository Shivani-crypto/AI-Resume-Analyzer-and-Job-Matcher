# AI Resume Analyzer and Job Matcher

## Project Description

AI Resume Analyzer and Job Matcher is a web-based application that helps users analyze resumes using Artificial Intelligence and Natural Language Processing (NLP).

The system extracts text from resumes, identifies skills, compares resumes with job descriptions, calculates matching scores, and provides AI-based suggestions to improve the resume.

It also generates interview questions based on the resume and job description.

---

## Features

- Upload Resume (PDF/DOCX/Image)
- Extract Resume Text
- Skill Extraction using NLP
- Resume vs Job Description Matching
- Matching Score Calculation
- Missing Skills Detection
- AI Suggestions for Improvement
- Pie Chart Visualization
- Interview Question Generation
- Simple and User-Friendly Interface

---

## Project Structure

```bash
resume_analyzer/
│
├── app.py
├── requirements.txt
├── static/
│   └── style.css
│
├── templates/
│   ├── index.html
│   ├── result.html
│
├── utils/
│   ├── extractor.py
│   ├── skills.py
│   ├── matcher.py
│   ├── ai_helper.py
│
├── uploads/

Technologies Used
Python
Flask
HTML/CSS
Machine Learning
NLP
Scikit-learn
PDF Processing
OCR (Tesseract)
Installation
Step 1: Clone the Repository
git clone <repository_link>
cd resume_analyzer
Step 2: Install Required Packages
pip install flask pdfplumber python-docx pytesseract pillow matplotlib scikit-learn
Step 3: Run the Application
python app.py
Step 4: Open Browser
http://127.0.0.1:5000
Workflow
Upload Resume
   ↓
Store File
   ↓
Click "Extract Text"
   ↓
Extract Text
   ↓
Show Extracted Text
   ↓
AI Suggestions
   ↓
Enter Job Description
   ↓
Compare Resume vs JD
   ↓
Show:
   - Score
   - Missing Skills
   - Suggestions
   - Pie Chart
   ↓
Generate Interview Questions
Modules Description
extractor.py

Extracts text from PDF, DOCX, and image files.

skills.py

Identifies technical skills from extracted text.

matcher.py

Calculates similarity score between resume and job description.

ai_helper.py

Generates AI suggestions and interview questions.

Future Enhancements
Login & Registration System
Resume Ranking System
Multiple Resume Comparison
AI Chatbot Support
Job Recommendation Engine
Cloud Deployment
Output
Resume Matching Score
Missing Skills
Resume Improvement Suggestions
Generated Interview Questions
Pie Chart Visualization
Author

Developed by Shivani
