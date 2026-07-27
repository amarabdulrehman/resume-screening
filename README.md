# RecruitAI — AI Resume Screening System

> An NLP-powered resume screening system that automatically analyzes uploaded resumes, extracts key candidate information, and ranks them against a job description using machine learning techniques.

---

## Features

- **PDF & DOCX** resume upload (multiple files at once)
- **NLP Information Extraction** — Name, Email, Phone, Skills, Education, Experience
- **Skills Detection** from a curated database of 150+ keywords
- **TF-IDF Cosine Similarity** for resume-to-JD text matching
- **Composite Scoring** — Text match (50%) + Skills overlap (40%) + Experience (10%)
- **Candidate Ranking** with visual score breakdowns and radar charts
- **SQLite Database** via SQLAlchemy (switchable to MySQL/PostgreSQL)
- **Premium Dark UI** — Bootstrap 5 + custom glassmorphism CSS

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.10+, Flask 3.x |
| NLP | NLTK, scikit-learn TF-IDF |
| Database | SQLAlchemy + SQLite |
| PDF Parsing | pdfplumber |
| DOCX Parsing | python-docx |
| Frontend | HTML5, Bootstrap 5, CSS3, Chart.js |

---

## Project Structure

```
internship_5/
├── app.py                  # Flask application factory
├── config.py               # Configuration (DB, upload folder)
├── extensions.py           # SQLAlchemy, Migrate instances
├── requirements.txt        # Python dependencies
├── README.md
├── models/
│   ├── candidate.py        # Candidate DB model
│   ├── job.py              # Job DB model
│   └── result.py           # ScreeningResult DB model
├── services/
│   ├── file_parser.py      # PDF/DOCX text extraction
│   ├── extractor.py        # NLP info extraction (NLTK + regex)
│   └── matcher.py          # TF-IDF matching + ranking engine
├── routes/
│   ├── main.py             # Dashboard routes
│   ├── resume.py           # Upload & candidate routes
│   └── job.py              # Job & screening routes
├── templates/
│   ├── base.html           # Shared layout (sidebar, topbar)
│   ├── index.html          # Dashboard
│   ├── upload.html         # Drag-and-drop upload
│   ├── candidates.html     # All candidates list
│   ├── job_form.html       # Post a job
│   ├── job_list.html       # All jobs
│   ├── job_detail.html     # Single job view
│   ├── results.html        # Ranked candidates
│   └── candidate_detail.html  # Full candidate profile
├── static/
│   ├── css/style.css       # Premium dark theme
│   ├── js/main.js          # Client-side interactions
│   └── uploads/            # Uploaded resume files
└── nlp_data/
    └── skills_db.json      # 150+ skills keyword database
```

---

## Setup & Run

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Application
```bash
python app.py
```

### 3. Open in Browser
```
http://127.0.0.1:5000
```

---

## Usage Workflow

1. **Upload Resumes** → `/resume/upload` — drag and drop PDF/DOCX files
2. **Create a Job** → `/job/new` — paste the job description + required skills
3. **Run Screening** → click "Run AI Screening" on the job detail page
4. **View Rankings** → ranked candidates with match scores, skill overlap, and breakdowns
5. **View Profiles** → individual candidate pages with radar chart

---

## Matching Algorithm

```
Match Score (0-100%) =
  50% × TF-IDF cosine similarity (resume text vs. JD text)
+ 40% × Skills overlap (candidate skills ∩ required skills)
+ 10% × Experience bonus (normalised years 0-10)
```

---

## Database Migration (MySQL/PostgreSQL)

Change one line in `config.py`:
```python
# MySQL
SQLALCHEMY_DATABASE_URI = "mysql+pymysql://user:pass@localhost/resume_db"

# PostgreSQL
SQLALCHEMY_DATABASE_URI = "postgresql://user:pass@localhost/resume_db"
```

---

## Author

Developed as an internship project demonstrating NLP, Flask web development,
and database-driven application design.
