"""
services/matcher.py — NLP Matching & Ranking Engine
======================================================
Calculates how well each candidate's resume matches a job description.

Composite Score (0–100):
  50% — TF-IDF cosine similarity (resume text vs. JD text)
  40% — Skills overlap (candidate skills ∩ JD required skills)
  10% — Experience bonus (years of experience normalised)
"""

import re
import math
from typing import List, Tuple

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ── Text Cleaning ─────────────────────────────────────────
def _clean(text: str) -> str:
    """Lowercase, strip non-alpha, collapse whitespace."""
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r"[^a-z\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


# ── TF-IDF Cosine Similarity ──────────────────────────────
def _tfidf_similarity(resume_text: str, jd_text: str) -> float:
    """
    Vectorise resume + JD with TF-IDF and compute cosine similarity.
    Returns a float in [0, 1].
    """
    corpus = [_clean(resume_text), _clean(jd_text)]
    if not any(corpus):
        return 0.0

    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        stop_words="english",
        min_df=1,
    )
    try:
        tfidf_matrix = vectorizer.fit_transform(corpus)
        score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        return float(score)
    except ValueError:
        return 0.0


# ── Skills Overlap ────────────────────────────────────────
def _skill_overlap(candidate_skills: list, required_skills: list) -> float:
    """
    Jaccard-style skill overlap:
      |candidate ∩ required| / |required|
    Falls back to TF-IDF overlap if required_skills list is empty.
    """
    if not required_skills:
        return 0.0
    cand_set = set(s.lower() for s in candidate_skills)
    req_set  = set(s.lower() for s in required_skills)
    if not req_set:
        return 0.0
    overlap = len(cand_set & req_set) / len(req_set)
    return min(overlap, 1.0)


# ── Experience Bonus ──────────────────────────────────────
def _experience_bonus(years: float, max_years: float = 10.0) -> float:
    """Normalise experience years to [0, 1]. Capped at max_years."""
    if years <= 0:
        return 0.0
    return min(years / max_years, 1.0)


# ── Composite Score ───────────────────────────────────────
def _composite_score(
    tfidf:   float,
    skills:  float,
    exp:     float,
    w_tfidf: float = 0.50,
    w_skills: float = 0.40,
    w_exp:   float = 0.10,
) -> float:
    """Weighted composite score scaled to 0–100."""
    raw = (w_tfidf * tfidf) + (w_skills * skills) + (w_exp * exp)
    return round(raw * 100, 2)


# ── Main Ranking Function ─────────────────────────────────
def rank_candidates(candidates, job) -> List[Tuple]:
    """
    Score and rank all candidates against a job.

    Parameters
    ----------
    candidates : list[Candidate]   — SQLAlchemy Candidate objects
    job        : Job               — SQLAlchemy Job object

    Returns
    -------
    List of (Candidate, scores_dict) sorted by match_score desc.
    """
    jd_text        = (job.description or "")
    required_skills = job.required_skills or []

    ranked = []
    for candidate in candidates:
        resume_text = candidate.raw_text or ""

        # If candidate has no text, give zero score
        if not resume_text.strip():
            scores = {
                "match_score":   0.0,
                "tfidf_score":   0.0,
                "skill_overlap": 0.0,
                "exp_bonus":     0.0,
            }
            ranked.append((candidate, scores))
            continue

        tfidf_score   = _tfidf_similarity(resume_text, jd_text)
        skill_overlap = _skill_overlap(
            candidate.skills, required_skills
        )
        exp_bonus     = _experience_bonus(candidate.experience_years or 0.0)
        match_score   = _composite_score(tfidf_score, skill_overlap, exp_bonus)

        scores = {
            "match_score":   match_score,
            "tfidf_score":   round(tfidf_score, 4),
            "skill_overlap": round(skill_overlap, 4),
            "exp_bonus":     round(exp_bonus, 4),
        }
        ranked.append((candidate, scores))

    # Sort by composite score descending
    ranked.sort(key=lambda x: x[1]["match_score"], reverse=True)
    return ranked
