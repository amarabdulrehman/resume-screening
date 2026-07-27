"""
services/extractor.py — NLP Information Extractor
===================================================
Extracts structured candidate information from raw resume text.
Uses regex + NLTK (no spaCy dependency — compatible with Python 3.14+):
  • Name        — NLTK POS tagging (NNP sequences) + heuristics
  • Email       — regex
  • Phone       — regex
  • Skills      — keyword matching against skills_db.json
  • Education   — section detection + keyword matching
  • Experience  — years regex + section text
"""

import re
import json
import os
from typing import Optional

# ── NLTK lazy-load ─────────────────────────────────────
_nltk_ready = False

def _ensure_nltk():
    global _nltk_ready
    if _nltk_ready:
        return
    import nltk
    for resource in ["punkt", "averaged_perceptron_tagger",
                     "punkt_tab", "averaged_perceptron_tagger_eng"]:
        try:
            nltk.data.find(f"tokenizers/{resource}")
        except LookupError:
            try:
                nltk.download(resource, quiet=True)
            except Exception:
                pass
    _nltk_ready = True


# ── Regex Patterns ───────────────────────────────────────
_EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")
_PHONE_RE = re.compile(
    r"(?:\+?\d{1,3}[\s\-\.]?)?"
    r"(?:\(?\d{3}\)?[\s\-\.]?)"
    r"\d{3}[\s\-\.]?\d{4}"
)
_EXP_YEARS_RE = re.compile(
    r"(\d+(?:\.\d+)?)\s*(?:\+)?\s*"
    r"(?:years?|yrs?)[\s\w]*?(?:experience|exp)?",
    re.IGNORECASE
)

_DEGREE_KEYWORDS = [
    "bachelor", "master", "phd", "ph.d", "b.s", "b.sc", "m.s", "m.sc",
    "b.e", "b.tech", "m.tech", "mba", "associate", "diploma", "degree",
    "computer science", "information technology", "engineering", "bcs",
    "bscs", "mscs", "b.com", "m.com", "bba",
]

_SECTION_HEADERS = {
    "experience":     ["experience", "work history", "employment", "career", "professional"],
    "education":      ["education", "academic", "qualification", "degree", "studies"],
    "skills":         ["skills", "technical skills", "competencies", "expertise", "technologies"],
    "projects":       ["projects", "portfolio", "work samples"],
    "certifications": ["certifications", "certificates", "licenses", "credentials"],
}

# Common non-name words to filter from name detection
_NON_NAME_WORDS = {
    "resume", "cv", "curriculum", "vitae", "profile", "summary",
    "objective", "contact", "email", "phone", "address", "linkedin",
    "github", "portfolio", "skills", "experience", "education",
}


def _load_skills_db(skills_db_path: str) -> list:
    if not os.path.exists(skills_db_path):
        return []
    with open(skills_db_path, "r", encoding="utf-8") as f:
        db = json.load(f)
    all_skills = []
    for cat_skills in db.values():
        all_skills.extend([s.lower() for s in cat_skills])
    return all_skills


def _extract_email(text: str) -> Optional[str]:
    m = _EMAIL_RE.search(text)
    return m.group(0).lower() if m else None


def _extract_phone(text: str) -> Optional[str]:
    m = _PHONE_RE.search(text)
    return m.group(0).strip() if m else None


def _extract_name(text: str) -> Optional[str]:
    """
    Name detection using two strategies:
    1. NLTK POS tagging — find consecutive proper noun (NNP) sequences
       in the first 300 chars (names are at top of resumes).
    2. Fallback: first clean line that looks like a name.
    """
    _ensure_nltk()
    try:
        import nltk
        snippet = text[:300]
        tokens  = nltk.word_tokenize(snippet)
        tagged  = nltk.pos_tag(tokens)

        # Collect consecutive NNP sequences (proper nouns)
        candidates = []
        current    = []
        for word, tag in tagged:
            if tag in ("NNP", "NNPS") and word.isalpha():
                current.append(word)
            else:
                if len(current) >= 2:
                    name = " ".join(current)
                    if not any(w.lower() in _NON_NAME_WORDS for w in current):
                        candidates.append(name)
                current = []
        if len(current) >= 2:
            name = " ".join(current)
            if not any(w.lower() in _NON_NAME_WORDS for w in current):
                candidates.append(name)

        if candidates:
            return candidates[0]

    except Exception:
        pass

    # Fallback: first short line that looks like a name
    for line in text.split("\n"):
        line = line.strip()
        words = line.split()
        if (2 <= len(words) <= 5
                and len(line) < 60
                and not _EMAIL_RE.search(line)
                and not _PHONE_RE.search(line)
                and not any(w.lower() in _NON_NAME_WORDS for w in words)
                and all(not w.isdigit() for w in words)):
            return line

    return None


def _extract_skills(text: str, skills_db_path: str) -> list:
    all_skills = _load_skills_db(skills_db_path)
    text_lower = text.lower()
    found = set()
    for skill in all_skills:
        if len(skill) <= 3:
            if re.search(r"\b" + re.escape(skill) + r"\b", text_lower):
                found.add(skill)
        else:
            if skill in text_lower:
                found.add(skill)
    return sorted(found)


def _split_sections(text: str) -> dict:
    lines   = text.split("\n")
    sections: dict = {"header": []}
    current = "header"
    for line in lines:
        stripped = line.strip().lower()
        matched  = False
        for section, keywords in _SECTION_HEADERS.items():
            if any(kw in stripped for kw in keywords) and len(stripped) < 50:
                current = section
                sections.setdefault(section, [])
                matched = True
                break
        if not matched:
            sections.setdefault(current, []).append(line)
    return {k: "\n".join(v).strip() for k, v in sections.items()}


def _extract_education(text: str, sections: dict) -> Optional[str]:
    edu_text  = sections.get("education", text)
    edu_lines = [
        l.strip() for l in edu_text.split("\n")
        if any(kw in l.lower() for kw in _DEGREE_KEYWORDS)
    ]
    return "; ".join(edu_lines[:5]) if edu_lines else edu_text[:300] or None


def _extract_experience_years(text: str) -> float:
    matches = _EXP_YEARS_RE.findall(text)
    return max((float(y) for y in matches), default=0.0)


def _extract_experience_text(sections: dict) -> Optional[str]:
    return sections.get("experience", "")[:1500] or None


# ── Main Entry Point ─────────────────────────────────────
def extract_candidate_info(raw_text: str, skills_db_path: str) -> dict:
    """
    Full NLP extraction pipeline.
    Returns: name, email, phone, skills, education, experience_years, experience_text.
    """
    sections = _split_sections(raw_text)
    return {
        "name":             _extract_name(raw_text),
        "email":            _extract_email(raw_text),
        "phone":            _extract_phone(raw_text),
        "skills":           _extract_skills(raw_text, skills_db_path),
        "education":        _extract_education(raw_text, sections),
        "experience_years": _extract_experience_years(raw_text),
        "experience_text":  _extract_experience_text(sections),
    }
