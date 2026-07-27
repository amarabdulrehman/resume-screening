import sys
sys.path.insert(0, '.')
from services.file_parser import parse_resume
from services.extractor import extract_candidate_info

path = r'C:\Users\rpmmu\OneDrive\Desktop\AmarAbdurrehman_resume.pdf'
print('[TEST] Parsing resume...')
text = parse_resume(path)
print(f'[OK] Extracted {len(text)} characters')
print('[TEST] Running NLP extraction...')
info = extract_candidate_info(text, 'nlp_data/skills_db.json')
print('  Name    :', info['name'])
print('  Email   :', info['email'])
print('  Phone   :', info['phone'])
print('  Skills  :', info['skills'][:10])
edu = str(info['education'] or '')
print('  Edu     :', edu[:80])
print('  Exp yrs :', info['experience_years'])
print('[DONE] Extraction pipeline works!')
