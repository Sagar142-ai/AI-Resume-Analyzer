from flask import Flask, render_template, request
import os
import PyPDF2

app = Flask(__name__)

# Folder to store resumes
UPLOAD_FOLDER = 'resumes'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Simple skills database
SKILLS_DB = [
    'python', 'java', 'sql', 'html', 'css',
    'javascript', 'flask', 'aws',
    'machine learning', 'ai'
]

# ---------- FUNCTIONS ----------

def extract_text_from_pdf(path):
    text = ""
    with open(path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            if page.extract_text():
                text += page.extract_text()
    return text.lower()

def extract_skills(text):
    skills = []
    for skill in SKILLS_DB:
        if skill in text:
            skills.append(skill)
    return skills

# ---------- ROUTES ----------

@app.route('/')
def home():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_resume():
    role = request.form['role']
    file = request.files['resume']

    if file:
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)

        path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(path)

        resume_text = extract_text_from_pdf(path)
        skills = extract_skills(resume_text)

        # Generate questions
        questions = []
        for skill in skills:
            questions.append(f"Explain your experience with {skill}")

        if not questions:
            questions = [
                f"What skills are required for a {role}?",
                "Explain one project you have worked on",
                "What are your strengths?"
            ]

        return render_template(
            'questions.html',
            role=role,
            skills=skills,
            questions=questions
        )

@app.route('/submit_answers', methods=['POST'])
def submit_answers():
    answers = request.form.to_dict()

    score = 0
    feedback = []

    for question, answer in answers.items():
        if len(answer.strip()) >= 30:
            score += 10
            feedback.append(f"{question} : Good answer")
        else:
            feedback.append(f"{question} : Answer needs improvement")

    return render_template(
        'result.html',
        score=score,
        feedback=feedback
    )

# ---------- RUN APP ----------

if __name__ == '__main__':
    app.run(debug=True)
