print("APP STARTED SUCCESSFULLY")
from flask import Flask, render_template_string, request


import os
import PyPDF2

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')

print("BASE DIR:", BASE_DIR)
print("TEMPLATE DIR:", TEMPLATE_DIR)
print("TEMPLATE FILES:", os.listdir(TEMPLATE_DIR))

app = Flask(__name__, template_folder=TEMPLATE_DIR)

UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def home():
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Resume Analyzer</title>
        <style>
            body {
                margin: 0;
                font-family: Arial, sans-serif;
                background: linear-gradient(120deg, #0f2027, #203a43, #2c5364);
                height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                color: white;
            }
            .container {
                background: rgba(255, 255, 255, 0.1);
                padding: 40px;
                border-radius: 15px;
                width: 400px;
                text-align: center;
                box-shadow: 0 0 25px rgba(0,0,0,0.4);
            }
            h1 {
                margin-bottom: 10px;
            }
            p {
                font-size: 14px;
                opacity: 0.9;
            }
            input[type=file] {
                margin-top: 20px;
                color: white;
            }
            button {
                margin-top: 20px;
                padding: 12px;
                width: 100%;
                border: none;
                border-radius: 25px;
                background: #00c6ff;
                color: black;
                font-size: 16px;
                font-weight: bold;
                cursor: pointer;
            }
            button:hover {
                background: #00a3cc;
            }
            footer {
                margin-top: 20px;
                font-size: 12px;
                opacity: 0.8;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 AI Resume Analyzer</h1>
            <p>Upload your resume and get AI-powered job recommendations</p>

            <form action="/upload" method="post" enctype="multipart/form-data">
                <input type="file" name="resume" required>
                <button type="submit">Analyze Resume</button>
            </form>

            <footer>
                Powered by AI & Cloud Computing
            </footer>
        </div>
    </body>
    </html>
    """)



@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['resume']

    if file:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        # Extract text from PDF
        text = ""
        with open(filepath, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                if page.extract_text():
                    text += page.extract_text().lower()

        # Skill list
        skills_list = [
            'python', 'java', 'c', 'c++', 'sql', 'html', 'css', 'javascript',
            'machine learning', 'data science', 'aws', 'flask', 'django',
            'react', 'node', 'git'
        ]

        found_skills = [skill for skill in skills_list if skill in text]

        # Job roles
        job_roles = {
            "Data Analyst": ["python", "sql", "excel", "power bi", "data analysis"],
            "Machine Learning Engineer": ["python", "machine learning", "data science"],
            "Web Developer": ["html", "css", "javascript", "react", "flask"],
            "Cloud Engineer": ["aws", "linux", "cloud"],
            "Software Developer": ["python", "java", "git", "sql"]
        }

        # Job role recommendation
        best_role = None
        max_match = 0

        for role, skills in job_roles.items():
            match_count = len(set(found_skills) & set(skills))
            if match_count > max_match:
                max_match = match_count
                best_role = role

        # Skill gap analysis
        missing_skills = []
        if best_role:
            required_skills = job_roles[best_role]
            missing_skills = [s for s in required_skills if s not in found_skills]
            return render_template_string("""
<!DOCTYPE html>
<html>
<head>
<title>AI Analysis Result</title>
<style>
body {
    background: #0f2027;
    color: white;
    font-family: Arial;
    padding: 30px;
}
.card {
    background: #203a43;
    padding: 25px;
    border-radius: 15px;
    max-width: 700px;
    margin: auto;
    box-shadow: 0 0 20px rgba(0,0,0,0.5);
}
h2 {
    color: #00c6ff;
}
ul {
    list-style: none;
    padding: 0;
}
li {
    background: #2c5364;
    margin: 5px 0;
    padding: 10px;
    border-radius: 8px;
}
.back {
    text-align: center;
    margin-top: 20px;
}
a {
    color: #00c6ff;
    text-decoration: none;
    font-weight: bold;
}
</style>
</head>
<body>

<div class="card">
    <h2>✅ Detected Skills</h2>
    <ul>
    {% for skill in skills %}
        <li>{{ skill }}</li>
    {% endfor %}
    </ul>

    <h2>🎯 Recommended Job Role</h2>
    <p><b>{{ role }}</b></p>

    <h2>📉 Missing Skills</h2>
    {% if missing %}
    <ul>
    {% for m in missing %}
        <li>{{ m }}</li>
    {% endfor %}
    </ul>
    {% else %}
    <p>No missing skills 🎉</p>
    {% endif %}

    <div class="back">
        <a href="/">⬅ Analyze Another Resume</a>
    </div>
</div>

</body>
</html>
""", skills=found_skills, role=best_role, missing=missing_skills)

            return "Upload failed"




if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)


