import sys
sys.path.insert(0, '.')
from app import app
from extensions import db
from models import Candidate
from services.file_parser import parse_resume
from services.extractor import extract_candidate_info
import os, shutil

UPLOAD_FOLDER = os.path.join('.', 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

resumes = [
    r'C:\Users\rpmmu\OneDrive\Desktop\AmarAbdurrehman_resume.pdf',
    r'C:\Users\rpmmu\OneDrive\Desktop\AmarAbdurrehman__resume.pdf',
    r'C:\Users\rpmmu\OneDrive\Desktop\Muhammad Sameer Akmal.pdf',
]

with app.app_context():
    for path in resumes:
        if not os.path.exists(path):
            print('Skipping (not found):', path)
            continue
        fname = os.path.basename(path)
        dest  = os.path.join(UPLOAD_FOLDER, fname)
        shutil.copy2(path, dest)
        raw  = parse_resume(dest)
        info = extract_candidate_info(raw, 'nlp_data/skills_db.json')
        c    = Candidate(
            name             = info['name'],
            email            = info['email'],
            phone            = info['phone'],
            education        = info['education'],
            experience_years = info['experience_years'],
            experience_text  = info['experience_text'],
            resume_filename  = fname,
            raw_text         = raw,
        )
        c.skills = info['skills']
        db.session.add(c)
        print('Added:', info['name'], '|', len(info['skills']), 'skills')
    db.session.commit()
    print('DB seeded successfully!')
