# AI Resume Analyzer

## Overview
This project analyzes PDF resumes and provides feedback on skills and keywords using Python, Flask, and NLP techniques.

## Features
- Extract text from PDF resumes
- Identify key skills across multiple categories (Programming Languages, Data Science, Cloud/DevOps, Databases, Web Development, Soft Skills)
- Provide improvement suggestions with a 0–100 resume score
- Clean, responsive web UI

## Tech Stack
- Python 3.9+
- Flask 3
- PyPDF2 (PDF text extraction)
- scikit-learn / NLP (skill pattern matching)
- HTML/CSS (responsive frontend)

## Project Structure

```
ai-resume-analyzer/
├── app.py                    # Flask application entry point
├── requirements.txt          # Python dependencies
├── resume_analyzer/
│   ├── __init__.py
│   ├── extractor.py          # PDF text extraction
│   ├── skill_identifier.py   # NLP-based skill identification
│   └── feedback.py           # Score calculation & feedback generation
├── templates/
│   ├── index.html            # Upload page
│   └── results.html          # Analysis results page
├── static/
│   └── style.css             # Responsive stylesheet
└── tests/
    └── test_analyzer.py      # Unit & integration tests
```

## Installation

```bash
# Clone the repository
git clone https://github.com/sadafdarwish/ai-resume-analyzer.git
cd ai-resume-analyzer

# Create and activate a virtual environment (recommended)
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Running the App

```bash
python app.py
```

Navigate to [http://localhost:5000](http://localhost:5000) in your browser, upload a PDF resume, and receive instant feedback.

## How It Works
1. **Upload resume** — choose a PDF file (max 5 MB) through the web UI.
2. **Text is processed** — PyPDF2 extracts all text from the PDF.
3. **Skills are extracted** — the NLP module matches known skill keywords across six categories.
4. **Feedback is generated** — a 0–100 score and actionable suggestions are returned.

## Running Tests

```bash
python -m pytest tests/ -v
```

## Future Improvements
- Add job-description matching to tailor feedback to a specific role
- Improve NLP model with TF-IDF and word embeddings
- Add support for DOCX resumes
- Export analysis report as PDF