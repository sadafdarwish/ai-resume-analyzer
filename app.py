"""Flask application entry point for AI Resume Analyzer."""

import os

from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from werkzeug.utils import secure_filename

from resume_analyzer import extract_text_from_pdf, generate_feedback, identify_skills

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
ALLOWED_EXTENSIONS = {"pdf"}
MAX_CONTENT_MB = 5  # Maximum upload size in megabytes

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_MB * 1024 * 1024

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _allowed_file(filename: str) -> bool:
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/", methods=["GET"])
def index():
    """Render the resume upload page."""
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    """Accept a PDF upload and return the analysis results page."""
    # Validate file presence.
    if "resume" not in request.files:
        flash("No file part in the request.", "error")
        return redirect(url_for("index"))

    file = request.files["resume"]

    if file.filename == "":
        flash("No file selected. Please choose a PDF resume.", "error")
        return redirect(url_for("index"))

    if not _allowed_file(file.filename):
        flash("Only PDF files are supported.", "error")
        return redirect(url_for("index"))

    filename = secure_filename(file.filename)
    save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(save_path)

    try:
        with open(save_path, "rb") as fh:
            resume_text = extract_text_from_pdf(fh)

        skills_by_category = identify_skills(resume_text)
        feedback = generate_feedback(skills_by_category, resume_text)

        return render_template(
            "results.html",
            filename=filename,
            resume_text=resume_text[:500] + ("…" if len(resume_text) > 500 else ""),
            skills_by_category=skills_by_category,
            feedback=feedback,
        )
    except ValueError as exc:
        flash(str(exc), "error")
        return redirect(url_for("index"))
    finally:
        # Remove the uploaded file after processing.
        if os.path.exists(save_path):
            os.remove(save_path)


@app.errorhandler(413)
def request_entity_too_large(error):
    flash(f"File too large. Maximum allowed size is {MAX_CONTENT_MB} MB.", "error")
    return redirect(url_for("index"))


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)
