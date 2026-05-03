from flask import Flask, request, render_template
import re

app = Flask(__name__)

def analyze_resume(text):
    skills = ["python", "java", "sql", "machine learning", "html", "css"]
    found = [skill for skill in skills if skill in text.lower()]
    return found

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        resume_text = request.form['resume']
        skills = analyze_resume(resume_text)
        return f"Skills found: {', '.join(skills)}"
    return '''
    <form method="post">
        <textarea name="resume" rows="10" cols="30"></textarea>
        <br><input type="submit">
    </form>
    '''

if __name__ == "__main__":
    app.run(debug=True)
