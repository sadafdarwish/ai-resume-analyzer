"""NLP-based skill identification from resume text."""

import re
from typing import Dict, List

# ---------------------------------------------------------------------------
# Skill taxonomy
# The lists below map a human-readable category name to a set of canonical
# skill keywords (lower-case).  All matching is case-insensitive so that
# "Python", "PYTHON" and "python" are all detected.
# ---------------------------------------------------------------------------

SKILL_TAXONOMY: Dict[str, List[str]] = {
    "Programming Languages": [
        "python", "java", "javascript", "typescript", "c", "c++", "c#",
        "ruby", "go", "golang", "rust", "swift", "kotlin", "scala",
        "r", "matlab", "perl", "php", "bash", "shell", "powershell",
    ],
    "Web Development": [
        "html", "css", "react", "angular", "vue", "vuejs", "node",
        "nodejs", "express", "django", "flask", "fastapi", "spring",
        "asp.net", "rails", "jquery", "bootstrap", "tailwind", "graphql",
        "rest", "restful", "api", "webpack", "next.js", "nuxt",
    ],
    "Data Science & Machine Learning": [
        "machine learning", "deep learning", "nlp", "natural language processing",
        "computer vision", "tensorflow", "pytorch", "keras", "scikit-learn",
        "sklearn", "pandas", "numpy", "scipy", "matplotlib", "seaborn",
        "xgboost", "lightgbm", "hugging face", "transformers", "bert",
        "data analysis", "data science", "statistics", "regression",
        "classification", "clustering", "neural network",
    ],
    "Databases": [
        "sql", "mysql", "postgresql", "postgres", "sqlite", "mongodb",
        "redis", "elasticsearch", "cassandra", "dynamodb", "oracle",
        "nosql", "database", "firebase", "supabase",
    ],
    "Cloud & DevOps": [
        "aws", "azure", "gcp", "google cloud", "docker", "kubernetes",
        "terraform", "ansible", "jenkins", "ci/cd", "devops", "linux",
        "unix", "nginx", "apache", "git", "github", "gitlab", "bitbucket",
        "helm", "prometheus", "grafana",
    ],
    "Soft Skills": [
        "communication", "leadership", "teamwork", "problem solving",
        "critical thinking", "project management", "agile", "scrum",
        "kanban", "time management", "collaboration", "adaptability",
        "creativity", "analytical", "presentation",
    ],
}

# Flat set for quick membership tests (used by get_all_detected_skills).


def _normalise(text: str) -> str:
    """Lower-case and collapse extra whitespace."""
    return re.sub(r"\s+", " ", text.lower().strip())


def identify_skills(text: str) -> Dict[str, List[str]]:
    """Identify skills mentioned in *text* and group them by category.

    Args:
        text: Plain-text resume content.

    Returns:
        A dict mapping category names to the list of detected skills in that
        category.  Categories with no matches are omitted.
    """
    normalised = _normalise(text)

    found: Dict[str, List[str]] = {}
    for category, skills in SKILL_TAXONOMY.items():
        detected = []
        for skill in skills:
            # Use word-boundary matching so "go" doesn't match "going"
            pattern = r"\b" + re.escape(skill) + r"\b"
            if re.search(pattern, normalised):
                detected.append(skill)
        if detected:
            found[category] = detected

    return found


def get_all_detected_skills(skills_by_category: Dict[str, List[str]]) -> List[str]:
    """Return a flat list of all detected skills across all categories."""
    return [
        skill
        for skills in skills_by_category.values()
        for skill in skills
    ]
