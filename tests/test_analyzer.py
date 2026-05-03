"""Tests for the resume_analyzer package and Flask application."""

import io
import os
import sys
import types
import unittest
from unittest.mock import MagicMock, patch

# ---------------------------------------------------------------------------
# Ensure the project root is on the path so imports work when running the
# tests directly (e.g. `python -m pytest tests/`).
# ---------------------------------------------------------------------------
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_pdf_bytes(text: str) -> bytes:
    """Create a minimal valid PDF that contains *text* (ASCII only)."""
    # We mock PyPDF2 in most tests, but this is used to exercise real paths.
    # For simplicity we rely on the mock below in PDF-extraction tests.
    return b"%PDF-1.4 fake"


# ===========================================================================
# skill_identifier tests
# ===========================================================================

class TestIdentifySkills(unittest.TestCase):
    def _identify(self, text):
        from resume_analyzer.skill_identifier import identify_skills
        return identify_skills(text)

    def test_detects_programming_language(self):
        result = self._identify("I am proficient in Python and JavaScript.")
        self.assertIn("Programming Languages", result)
        self.assertIn("python", result["Programming Languages"])
        self.assertIn("javascript", result["Programming Languages"])

    def test_detects_data_science_skills(self):
        result = self._identify(
            "Experienced with machine learning, pandas, and scikit-learn."
        )
        self.assertIn("Data Science & Machine Learning", result)
        skills = result["Data Science & Machine Learning"]
        self.assertIn("machine learning", skills)
        self.assertIn("pandas", skills)
        self.assertIn("scikit-learn", skills)

    def test_detects_cloud_devops(self):
        result = self._identify("Deployed on AWS using Docker and Kubernetes.")
        self.assertIn("Cloud & DevOps", result)
        skills = result["Cloud & DevOps"]
        self.assertIn("aws", skills)
        self.assertIn("docker", skills)

    def test_case_insensitive(self):
        result = self._identify("Expert in PYTHON and DOCKER.")
        self.assertIn("Programming Languages", result)
        self.assertIn("python", result["Programming Languages"])
        self.assertIn("Cloud & DevOps", result)
        self.assertIn("docker", result["Cloud & DevOps"])

    def test_no_false_positive_for_substrings(self):
        # "go" should not match "going" or "logo"
        result = self._identify("I am going to the store with a logo.")
        prog = result.get("Programming Languages", [])
        self.assertNotIn("go", prog)

    def test_empty_text_returns_empty_dict(self):
        result = self._identify("")
        self.assertEqual(result, {})

    def test_detects_soft_skills(self):
        result = self._identify("Strong communication and leadership skills.")
        self.assertIn("Soft Skills", result)
        self.assertIn("communication", result["Soft Skills"])
        self.assertIn("leadership", result["Soft Skills"])

    def test_get_all_detected_skills(self):
        from resume_analyzer.skill_identifier import (
            get_all_detected_skills,
            identify_skills,
        )
        skills_by_cat = identify_skills("Python, Docker, SQL expert.")
        flat = get_all_detected_skills(skills_by_cat)
        self.assertIn("python", flat)
        self.assertIn("docker", flat)
        self.assertIn("sql", flat)


# ===========================================================================
# feedback tests
# ===========================================================================

class TestCalculateScore(unittest.TestCase):
    def _score(self, skills_by_cat):
        from resume_analyzer.feedback import calculate_score
        return calculate_score(skills_by_cat)

    def test_empty_skills_gives_zero(self):
        self.assertEqual(self._score({}), 0)

    def test_full_coverage_gives_high_score(self):
        skills = {
            "Programming Languages": ["python", "java"],
            "Web Development": ["react", "django"],
            "Data Science & Machine Learning": ["machine learning", "pandas"],
            "Databases": ["sql", "postgresql"],
            "Cloud & DevOps": ["docker", "aws"],
            "Soft Skills": ["communication", "leadership"],
        }
        score = self._score(skills)
        self.assertGreaterEqual(score, 80)

    def test_score_is_bounded(self):
        skills = {cat: ["a", "b", "c", "d"] for cat in
                  ["Programming Languages", "Web Development",
                   "Data Science & Machine Learning", "Databases",
                   "Cloud & DevOps", "Soft Skills"]}
        score = self._score(skills)
        self.assertLessEqual(score, 100)
        self.assertGreaterEqual(score, 0)


class TestGenerateFeedback(unittest.TestCase):
    def _feedback(self, skills_by_cat, text=""):
        from resume_analyzer.feedback import generate_feedback
        return generate_feedback(skills_by_cat, text)

    def test_returns_required_keys(self):
        result = self._feedback({}, "some text")
        for key in ("score", "rating", "strengths", "improvements", "missing_categories"):
            self.assertIn(key, result)

    def test_empty_skills_lists_missing_categories(self):
        result = self._feedback({}, "")
        self.assertGreater(len(result["missing_categories"]), 0)

    def test_rating_excellent_when_high_score(self):
        skills = {
            "Programming Languages": ["python", "java"],
            "Web Development": ["react", "django"],
            "Data Science & Machine Learning": ["machine learning", "pandas"],
            "Databases": ["sql", "postgresql"],
            "Cloud & DevOps": ["docker", "aws"],
            "Soft Skills": ["communication", "leadership"],
        }
        result = self._feedback(skills, "python java react django machine learning")
        self.assertEqual(result["rating"], "Excellent")

    def test_short_resume_triggers_improvement(self):
        result = self._feedback({}, "short resume")
        improvement_text = " ".join(result["improvements"])
        self.assertIn("short", improvement_text.lower())

    def test_missing_email_triggers_improvement(self):
        result = self._feedback({}, "No email in this resume text at all.")
        improvement_text = " ".join(result["improvements"])
        self.assertIn("email", improvement_text.lower())

    def test_missing_experience_section_triggers_improvement(self):
        result = self._feedback({}, "Education: BSc Computer Science")
        improvement_text = " ".join(result["improvements"])
        self.assertIn("experience", improvement_text.lower())


# ===========================================================================
# extractor tests  (PyPDF2 is mocked)
# ===========================================================================

class TestExtractTextFromPdf(unittest.TestCase):
    def _extract(self, stream):
        from resume_analyzer.extractor import extract_text_from_pdf
        return extract_text_from_pdf(stream)

    def _mock_reader(self, pages_text):
        """Return a mock PdfReader whose pages yield the given texts."""
        mock_page = MagicMock()
        mock_reader = MagicMock()
        mock_reader.pages = [
            MagicMock(**{"extract_text.return_value": t}) for t in pages_text
        ]
        return mock_reader

    @patch("resume_analyzer.extractor.PyPDF2.PdfReader")
    def test_extracts_text_from_single_page(self, MockReader):
        MockReader.return_value = self._mock_reader(["Hello World"])
        result = self._extract(io.BytesIO(b"fake"))
        self.assertEqual(result, "Hello World")

    @patch("resume_analyzer.extractor.PyPDF2.PdfReader")
    def test_joins_multiple_pages(self, MockReader):
        MockReader.return_value = self._mock_reader(["Page one", "Page two"])
        result = self._extract(io.BytesIO(b"fake"))
        self.assertIn("Page one", result)
        self.assertIn("Page two", result)

    @patch("resume_analyzer.extractor.PyPDF2.PdfReader")
    def test_raises_on_empty_pdf(self, MockReader):
        MockReader.return_value = self._mock_reader([None, None])
        from resume_analyzer.extractor import extract_text_from_pdf
        with self.assertRaises(ValueError):
            extract_text_from_pdf(io.BytesIO(b"fake"))

    @patch("resume_analyzer.extractor.PyPDF2.PdfReader", side_effect=Exception("bad pdf"))
    def test_raises_on_corrupt_pdf(self, MockReader):
        from resume_analyzer.extractor import extract_text_from_pdf
        with self.assertRaises(ValueError):
            extract_text_from_pdf(io.BytesIO(b"not a pdf"))


# ===========================================================================
# Flask app tests
# ===========================================================================

class TestFlaskApp(unittest.TestCase):
    def setUp(self):
        import app as flask_app
        flask_app.app.config["TESTING"] = True
        flask_app.app.config["WTF_CSRF_ENABLED"] = False
        self.client = flask_app.app.test_client()

    def test_index_returns_200(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"AI Resume Analyzer", response.data)

    def test_analyze_no_file_redirects(self):
        response = self.client.post("/analyze", data={}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"No file", response.data)

    def test_analyze_empty_filename_redirects(self):
        data = {"resume": (io.BytesIO(b""), "")}
        response = self.client.post(
            "/analyze", data=data,
            content_type="multipart/form-data",
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"No file selected", response.data)

    def test_analyze_non_pdf_rejected(self):
        data = {"resume": (io.BytesIO(b"hello"), "resume.txt")}
        response = self.client.post(
            "/analyze", data=data,
            content_type="multipart/form-data",
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"PDF", response.data)

    @patch("app.extract_text_from_pdf", return_value="Python developer with AWS experience.")
    @patch("app.identify_skills", return_value={"Programming Languages": ["python"], "Cloud & DevOps": ["aws"]})
    @patch("app.generate_feedback", return_value={
        "score": 40,
        "rating": "Fair",
        "strengths": ["Good Python"],
        "improvements": ["Add more skills"],
        "missing_categories": ["Databases"],
    })
    def test_analyze_valid_pdf_returns_results(self, mock_fb, mock_skills, mock_extract):
        data = {"resume": (io.BytesIO(b"%PDF-1.4 fake"), "resume.pdf")}
        response = self.client.post(
            "/analyze", data=data,
            content_type="multipart/form-data",
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"resume.pdf", response.data)
        self.assertIn(b"Fair", response.data)


if __name__ == "__main__":
    unittest.main()
