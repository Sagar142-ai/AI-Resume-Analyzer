import os
import re
import uuid

import PyPDF2
from flask import Flask, render_template_string, request
from werkzeug.utils import secure_filename


# ============================================================
# APPLICATION CONFIGURATION
# ============================================================

print("APP STARTED SUCCESSFULLY")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")

# Create upload directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Maximum upload size: 5 MB
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

print("BASE DIR:", BASE_DIR)
print("UPLOAD FOLDER:", UPLOAD_FOLDER)


# ============================================================
# ALLOWED FILE TYPES
# ============================================================

ALLOWED_EXTENSIONS = {"pdf"}


def allowed_file(filename):
    """
    Check whether the uploaded file has an allowed extension.
    """

    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


# ============================================================
# SKILLS DATABASE
# ============================================================

SKILLS_LIST = [
    "python",
    "java",
    "c",
    "c++",
    "c#",
    "sql",
    "html",
    "css",
    "javascript",
    "typescript",
    "machine learning",
    "deep learning",
    "data science",
    "data analysis",
    "excel",
    "power bi",
    "tableau",
    "aws",
    "azure",
    "gcp",
    "linux",
    "flask",
    "django",
    "react",
    "node.js",
    "git",
    "github",
    "docker",
    "kubernetes",
    "mongodb",
    "mysql",
    "postgresql",
    "pandas",
    "numpy",
    "scikit-learn",
    "tensorflow",
    "pytorch",
    "spark",
    "hadoop",
    "rest api",
    "fastapi"
]


# ============================================================
# JOB ROLE DATABASE
# ============================================================

JOB_ROLES = {

    "Data Analyst": [
        "python",
        "sql",
        "excel",
        "power bi",
        "tableau",
        "pandas",
        "numpy",
        "data analysis"
    ],

    "Machine Learning Engineer": [
        "python",
        "machine learning",
        "deep learning",
        "data science",
        "pandas",
        "numpy",
        "scikit-learn",
        "tensorflow",
        "pytorch"
    ],

    "Web Developer": [
        "html",
        "css",
        "javascript",
        "typescript",
        "react",
        "node.js",
        "flask",
        "django",
        "rest api"
    ],

    "Cloud Engineer": [
        "aws",
        "azure",
        "gcp",
        "linux",
        "docker",
        "kubernetes",
        "python"
    ],

    "Software Developer": [
        "python",
        "java",
        "c++",
        "javascript",
        "sql",
        "git",
        "github",
        "rest api"
    ],

    "Data Scientist": [
        "python",
        "sql",
        "machine learning",
        "data science",
        "pandas",
        "numpy",
        "scikit-learn",
        "tensorflow",
        "statistics"
    ],

    "Backend Developer": [
        "python",
        "java",
        "flask",
        "django",
        "fastapi",
        "node.js",
        "sql",
        "mongodb",
        "rest api"
    ],

    "DevOps Engineer": [
        "linux",
        "aws",
        "docker",
        "kubernetes",
        "git",
        "github",
        "python"
    ]
}


# ============================================================
# SKILL MATCHING
# ============================================================

def contains_skill(text, skill):
    """
    Detect a skill inside resume text.

    Regex is used for short skills such as:
    C, C++, Java, SQL, Git, AWS

    This prevents false matches.
    """

    # Special handling for C++
    if skill == "c++":
        return bool(re.search(r"(?<!\w)c\+\+(?!\w)", text))

    # Special handling for C#
    if skill == "c#":
        return bool(re.search(r"(?<!\w)c#(?!\w)", text))

    # Special handling for C
    if skill == "c":
        return bool(re.search(r"(?<!\w)c(?!\w)", text))

    # Node.js
    if skill == "node.js":
        return bool(
            re.search(
                r"\bnode\s*\.?\s*js\b",
                text
            )
        )

    # Normal word/phrase matching
    pattern = r"(?<!\w)" + re.escape(skill) + r"(?!\w)"

    return bool(re.search(pattern, text))


def detect_skills(text):
    """
    Detect skills from resume text.
    """

    found_skills = []

    for skill in SKILLS_LIST:

        if contains_skill(text, skill):

            found_skills.append(skill)

    return found_skills


# ============================================================
# JOB ROLE ANALYSIS
# ============================================================

def analyze_job_roles(found_skills):
    """
    Compare detected skills with required skills
    for each job role.
    """

    role_results = []

    found_set = set(found_skills)

    for role, required_skills in JOB_ROLES.items():

        required_set = set(required_skills)

        matched = found_set.intersection(required_set)

        missing = required_set - found_set

        if required_set:

            percentage = (
                len(matched) / len(required_set)
            ) * 100

        else:

            percentage = 0

        role_results.append({

            "role": role,

            "matched": sorted(matched),

            "missing": sorted(missing),

            "percentage": round(percentage, 1),

            "matched_count": len(matched),

            "total_required": len(required_set)
        })

    # Highest matching role first
    role_results.sort(
        key=lambda x: x["percentage"],
        reverse=True
    )

    return role_results


# ============================================================
# ATS SCORE
# ============================================================

def calculate_ats_score(
    found_skills,
    text,
    best_role_percentage
):
    """
    Calculate a simple ATS-style score.

    This is not a real commercial ATS algorithm.
    It is a rule-based score for this project.
    """

    score = 0

    # Skill score
    skill_score = min(
        len(found_skills) * 4,
        40
    )

    score += skill_score

    # Resume length/content score
    word_count = len(text.split())

    if word_count >= 500:

        score += 20

    elif word_count >= 300:

        score += 15

    elif word_count >= 150:

        score += 10

    elif word_count >= 75:

        score += 5

    # Job role match
    score += int(
        best_role_percentage * 0.3
    )

    # Important resume keywords
    important_sections = [
        "education",
        "experience",
        "skills",
        "project",
        "projects",
        "certification",
        "certifications"
    ]

    section_count = sum(
        1
        for section in important_sections
        if section in text
    )

    score += min(
        section_count * 3,
        15
    )

    # Maximum score
    score = min(score, 100)

    return score


# ============================================================
# HOME PAGE
# ============================================================

@app.route("/")
def home():

    return render_template_string(
        """
<!DOCTYPE html>

<html>

<head>

    <title>AI Resume Analyzer</title>

    <meta name="viewport"
          content="width=device-width, initial-scale=1.0">

    <style>

        * {
            box-sizing: border-box;
        }

        body {

            margin: 0;

            font-family: Arial, sans-serif;

            background:
                linear-gradient(
                    120deg,
                    #0f2027,
                    #203a43,
                    #2c5364
                );

            min-height: 100vh;

            display: flex;

            justify-content: center;

            align-items: center;

            color: white;

            padding: 20px;
        }

        .container {

            background:
                rgba(255, 255, 255, 0.10);

            padding: 40px;

            border-radius: 20px;

            width: 100%;

            max-width: 500px;

            text-align: center;

            box-shadow:
                0 0 30px
                rgba(0,0,0,0.5);

            backdrop-filter: blur(10px);
        }

        h1 {

            margin-bottom: 10px;

            font-size: 32px;
        }

        p {

            font-size: 15px;

            opacity: 0.9;

            line-height: 1.6;
        }

        .upload-box {

            margin-top: 25px;

            padding: 25px;

            border: 2px dashed
                rgba(255,255,255,0.4);

            border-radius: 15px;
        }

        input[type=file] {

            width: 100%;

            margin-top: 10px;

            padding: 10px;

            color: white;
        }

        button {

            margin-top: 20px;

            padding: 14px;

            width: 100%;

            border: none;

            border-radius: 30px;

            background: #00c6ff;

            color: black;

            font-size: 16px;

            font-weight: bold;

            cursor: pointer;

            transition: 0.3s;
        }

        button:hover {

            background: #00a3cc;

            transform: translateY(-2px);
        }

        .info {

            margin-top: 15px;

            font-size: 12px;

            opacity: 0.7;
        }

        footer {

            margin-top: 25px;

            font-size: 12px;

            opacity: 0.7;
        }

    </style>

</head>

<body>

    <div class="container">

        <h1>🤖 AI Resume Analyzer</h1>

        <p>
            Upload your resume and get
            skill detection, job recommendations,
            ATS-style scoring and skill-gap analysis.
        </p>

        <div class="upload-box">

            <form
                action="/upload"
                method="post"
                enctype="multipart/form-data"
            >

                <input
                    type="file"
                    name="resume"
                    accept=".pdf"
                    required
                >

                <button type="submit">
                    🚀 Analyze Resume
                </button>

            </form>

            <div class="info">
                Maximum file size: 5 MB
                <br>
                PDF files only
            </div>

        </div>

        <footer>
            Powered by Flask • Python • PyPDF2
        </footer>

    </div>

</body>

</html>
"""
    )


# ============================================================
# UPLOAD AND ANALYZE RESUME
# ============================================================

@app.route("/upload", methods=["POST"])
def upload():

    # --------------------------------------------------------
    # Check whether file exists
    # --------------------------------------------------------

    if "resume" not in request.files:

        return "No resume file uploaded.", 400

    file = request.files["resume"]

    # --------------------------------------------------------
    # Check filename
    # --------------------------------------------------------

    if not file.filename:

        return "No file selected.", 400

    # --------------------------------------------------------
    # Check extension
    # --------------------------------------------------------

    if not allowed_file(file.filename):

        return "Only PDF files are allowed.", 400

    # --------------------------------------------------------
    # Secure filename
    # --------------------------------------------------------

    original_filename = secure_filename(
        file.filename
    )

    if not original_filename:

        return "Invalid filename.", 400

    # --------------------------------------------------------
    # Generate unique filename
    # --------------------------------------------------------

    unique_filename = (
        str(uuid.uuid4())
        + "_"
        + original_filename
    )

    filepath = os.path.join(
        app.config["UPLOAD_FOLDER"],
        unique_filename
    )

    # --------------------------------------------------------
    # Save file
    # --------------------------------------------------------

    try:

        file.save(filepath)

    except Exception as e:

        return (
            f"Could not save uploaded file: {str(e)}",
            500
        )

    # --------------------------------------------------------
    # Extract PDF text
    # --------------------------------------------------------

    text = ""

    try:

        with open(filepath, "rb") as f:

            reader = PyPDF2.PdfReader(f)

            if reader.is_encrypted:

                return (
                    "Encrypted PDFs are not supported.",
                    400
                )

            for page in reader.pages:

                page_text = page.extract_text()

                if page_text:

                    text += page_text + "\n"

    except Exception as e:

        return (
            f"Error reading PDF: {str(e)}",
            400
        )

    # --------------------------------------------------------
    # Clean extracted text
    # --------------------------------------------------------

    text = text.lower()

    text = re.sub(
        r"\s+",
        " ",
        text
    ).strip()

    # --------------------------------------------------------
    # Check whether text was extracted
    # --------------------------------------------------------

    if not text:

        return (
            """
            <h2>Could not extract text from this PDF.</h2>
            <p>
                Please upload a text-based PDF resume.
            </p>
            <a href="/">Go Back</a>
            """,
            400
        )

    # --------------------------------------------------------
    # Detect skills
    # --------------------------------------------------------

    found_skills = detect_skills(text)

    # --------------------------------------------------------
    # Analyze job roles
    # --------------------------------------------------------

    role_results = analyze_job_roles(
        found_skills
    )

    # --------------------------------------------------------
    # Best role
    # --------------------------------------------------------

    if role_results:

        best_role_data = role_results[0]

        best_role = best_role_data["role"]

        best_role_percentage = (
            best_role_data["percentage"]
        )

        missing_skills = (
            best_role_data["missing"]
        )

    else:

        best_role = "No suitable role found"

        best_role_percentage = 0

        missing_skills = []

    # --------------------------------------------------------
    # ATS score
    # --------------------------------------------------------

    ats_score = calculate_ats_score(
        found_skills,
        text,
        best_role_percentage
    )

    # --------------------------------------------------------
    # Resume statistics
    # --------------------------------------------------------

    word_count = len(text.split())

    # --------------------------------------------------------
    # Render results
    # --------------------------------------------------------

    return render_template_string(
        """
<!DOCTYPE html>

<html>

<head>

    <title>Resume Analysis Result</title>

    <meta name="viewport"
          content="width=device-width, initial-scale=1.0">

    <style>

        * {
            box-sizing: border-box;
        }

        body {

            margin: 0;

            background:
                linear-gradient(
                    120deg,
                    #0f2027,
                    #203a43,
                    #2c5364
                );

            color: white;

            font-family: Arial, sans-serif;

            padding: 30px;
        }

        .container {

            max-width: 1000px;

            margin: auto;
        }

        .header {

            text-align: center;

            margin-bottom: 30px;
        }

        .header h1 {

            color: #00c6ff;
        }

        .grid {

            display: grid;

            grid-template-columns:
                repeat(
                    auto-fit,
                    minmax(250px, 1fr)
                );

            gap: 20px;

            margin-bottom: 25px;
        }

        .card {

            background: #203a43;

            padding: 25px;

            border-radius: 15px;

            box-shadow:
                0 0 20px
                rgba(0,0,0,0.4);
        }

        .score {

            font-size: 50px;

            font-weight: bold;

            color: #00c6ff;

            text-align: center;
        }

        .score-label {

            text-align: center;

            opacity: 0.8;
        }

        h2 {

            color: #00c6ff;

            margin-top: 0;
        }

        ul {

            list-style: none;

            padding: 0;
        }

        li {

            background: #2c5364;

            margin: 7px 0;

            padding: 10px;

            border-radius: 8px;
        }

        .role {

            font-size: 25px;

            font-weight: bold;

            text-align: center;

            margin: 15px 0;
        }

        .percentage {

            font-size: 22px;

            color: #00c6ff;

            text-align: center;
        }

        .progress {

            width: 100%;

            height: 15px;

            background: #142b33;

            border-radius: 10px;

            overflow: hidden;

            margin-top: 10px;
        }

        .progress-bar {

            height: 100%;

            background: #00c6ff;

            width: {{ role_percentage }}%;
        }

        .role-list {

            margin-top: 15px;
        }

        .role-item {

            background: #2c5364;

            padding: 15px;

            border-radius: 10px;

            margin-bottom: 10px;
        }

        .role-name {

            font-weight: bold;

            font-size: 17px;
        }

        .role-percent {

            float: right;

            color: #00c6ff;

            font-weight: bold;
        }

        .back {

            text-align: center;

            margin-top: 30px;
        }

        .back a {

            display: inline-block;

            padding: 12px 25px;

            background: #00c6ff;

            color: black;

            border-radius: 25px;

            text-decoration: none;

            font-weight: bold;
        }

        .back a:hover {

            background: #00a3cc;
        }

        .empty {

            opacity: 0.7;
        }

    </style>

</head>

<body>

<div class="container">

    <div class="header">

        <h1>
            📊 Resume Analysis Report
        </h1>

        <p>
            Analysis completed successfully
        </p>

    </div>


    <!-- TOP STATISTICS -->

    <div class="grid">

        <div class="card">

            <div class="score">
                {{ ats_score }}
            </div>

            <div class="score-label">
                ATS-Style Score / 100
            </div>

        </div>


        <div class="card">

            <div class="score">
                {{ skills_count }}
            </div>

            <div class="score-label">
                Skills Detected
            </div>

        </div>


        <div class="card">

            <div class="score">
                {{ word_count }}
            </div>

            <div class="score-label">
                Resume Words
            </div>

        </div>

    </div>


    <!-- RECOMMENDED ROLE -->

    <div class="card">

        <h2>
            🎯 Recommended Job Role
        </h2>

        <div class="role">
            {{ best_role }}
        </div>

        <div class="percentage">

            {{ role_percentage }}%
            Skill Match

        </div>

        <div class="progress">

            <div class="progress-bar"></div>

        </div>

    </div>


    <br>


    <!-- DETECTED SKILLS -->

    <div class="card">

        <h2>
            ✅ Detected Skills
        </h2>

        {% if skills %}

            <ul>

            {% for skill in skills %}

                <li>
                    {{ skill }}
                </li>

            {% endfor %}

            </ul>

        {% else %}

            <p class="empty">
                No known skills were detected.
            </p>

        {% endif %}

    </div>


    <br>


    <!-- MISSING SKILLS -->

    <div class="card">

        <h2>
            📉 Skills You Should Improve
        </h2>

        {% if missing %}

            <ul>

            {% for skill in missing %}

                <li>
                    {{ skill }}
                </li>

            {% endfor %}

            </ul>

        {% else %}

            <p>
                🎉 No major missing skills detected
                for this role.
            </p>

        {% endif %}

    </div>


    <br>


    <!-- ALL JOB ROLE MATCHES -->

    <div class="card">

        <h2>
            💼 Job Role Compatibility
        </h2>

        <div class="role-list">

        {% for result in role_results %}

            <div class="role-item">

                <span class="role-name">
                    {{ result.role }}
                </span>

                <span class="role-percent">
                    {{ result.percentage }}%
                </span>

                <br>

                <small>
                    {{ result.matched_count }}
                    /
                    {{ result.total_required }}
                    skills matched
                </small>

            </div>

        {% endfor %}

        </div>

    </div>


    <!-- BACK BUTTON -->

    <div class="back">

        <a href="/">
            ⬅ Analyze Another Resume
        </a>

    </div>

</div>

</body>

</html>
""",

        ats_score=ats_score,

        skills=found_skills,

        skills_count=len(found_skills),

        word_count=word_count,

        best_role=best_role,

        role_percentage=best_role_percentage,

        missing=missing_skills,

        role_results=role_results
    )


# ============================================================
# ERROR HANDLER - FILE TOO LARGE
# ============================================================

@app.errorhandler(413)
def file_too_large(error):

    return (
        """
        <h2>File Too Large</h2>

        <p>
            Please upload a PDF smaller than 5 MB.
        </p>

        <a href="/">
            Go Back
        </a>
        """,
        413
    )


# ============================================================
# APPLICATION START
# ============================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,
        use_reloader=False
    )