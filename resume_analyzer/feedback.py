"""Feedback and improvement suggestions for resume analysis."""

from typing import Dict, List

# ---------------------------------------------------------------------------
# Category weights — used to score how well a resume covers each area.
# ---------------------------------------------------------------------------
CATEGORY_WEIGHTS: Dict[str, float] = {
    "Programming Languages": 0.20,
    "Web Development": 0.15,
    "Data Science & Machine Learning": 0.20,
    "Databases": 0.15,
    "Cloud & DevOps": 0.15,
    "Soft Skills": 0.15,
}

# Suggested skills to add when a category is weak or missing.
SUGGESTED_SKILLS: Dict[str, List[str]] = {
    "Programming Languages": ["Python", "JavaScript", "SQL"],
    "Web Development": ["REST APIs", "React", "Node.js"],
    "Data Science & Machine Learning": ["scikit-learn", "pandas", "TensorFlow"],
    "Databases": ["SQL", "PostgreSQL", "MongoDB"],
    "Cloud & DevOps": ["Docker", "AWS", "Git"],
    "Soft Skills": ["Communication", "Agile", "Problem Solving"],
}

# Minimum number of skills per category to be considered "good".
MIN_SKILLS_PER_CATEGORY = 2

# Overall score thresholds.
SCORE_EXCELLENT = 80
SCORE_GOOD = 55
SCORE_FAIR = 30


def calculate_score(skills_by_category: Dict[str, List[str]]) -> int:
    """Compute a 0-100 resume score based on skill coverage.

    Each category contributes a weighted proportion based on how many skills
    were found relative to the minimum threshold for that category.
    """
    total = 0.0
    for category, weight in CATEGORY_WEIGHTS.items():
        found = len(skills_by_category.get(category, []))
        # Cap contribution at the minimum threshold to avoid one category
        # dominating the score.
        coverage = min(found / MIN_SKILLS_PER_CATEGORY, 1.0)
        total += coverage * weight * 100

    return round(total)


def generate_feedback(
    skills_by_category: Dict[str, List[str]],
    resume_text: str,
) -> Dict:
    """Generate structured feedback for a resume.

    Args:
        skills_by_category: Output of ``identify_skills``.
        resume_text: Raw text of the resume (used for length/structure checks).

    Returns:
        A dict with keys:
            - ``score`` (int 0-100)
            - ``rating`` (str: Excellent / Good / Fair / Needs Improvement)
            - ``strengths`` (list[str])
            - ``improvements`` (list[str])
            - ``missing_categories`` (list[str])
    """
    score = calculate_score(skills_by_category)

    # Determine rating label.
    if score >= SCORE_EXCELLENT:
        rating = "Excellent"
    elif score >= SCORE_GOOD:
        rating = "Good"
    elif score >= SCORE_FAIR:
        rating = "Fair"
    else:
        rating = "Needs Improvement"

    strengths: List[str] = []
    improvements: List[str] = []
    missing_categories: List[str] = []

    # Strengths — categories where multiple skills were found.
    for category, skills in skills_by_category.items():
        if len(skills) >= MIN_SKILLS_PER_CATEGORY:
            strengths.append(
                f"Strong {category} coverage ({', '.join(skills[:3])}{'…' if len(skills) > 3 else ''})"
            )
        else:
            improvements.append(
                f"Expand {category} skills — consider adding: "
                + ", ".join(SUGGESTED_SKILLS.get(category, []))
            )

    # Missing categories.
    for category in CATEGORY_WEIGHTS:
        if category not in skills_by_category:
            missing_categories.append(category)
            improvements.append(
                f"No {category} skills detected — consider highlighting: "
                + ", ".join(SUGGESTED_SKILLS.get(category, []))
            )

    # Length check.
    word_count = len(resume_text.split())
    if word_count < 150:
        improvements.append(
            "Your resume appears quite short. Aim for at least 300–500 words to "
            "give recruiters enough information."
        )
    elif word_count > 1000:
        strengths.append("Comprehensive resume with detailed content.")

    # Contact / section checks (simple heuristics).
    lower = resume_text.lower()
    if "experience" not in lower and "work history" not in lower:
        improvements.append(
            "Consider adding an 'Experience' or 'Work History' section."
        )
    if "education" not in lower:
        improvements.append("Consider adding an 'Education' section.")
    if "@" not in resume_text:
        improvements.append(
            "No email address detected — make sure your contact information is included."
        )

    if not strengths:
        strengths.append("Resume successfully parsed and analysed.")

    return {
        "score": score,
        "rating": rating,
        "strengths": strengths,
        "improvements": improvements,
        "missing_categories": missing_categories,
    }
