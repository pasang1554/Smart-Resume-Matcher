# Smart Resume Matcher

Smart Resume Matcher is a Streamlit-based resume screening app that compares uploaded resumes against a job description, scores candidates, highlights missing skills, and presents a shortlist in a clean dashboard.

## Features
- Resume-to-job matching using TF-IDF similarity
- Skill extraction and missing-skill analysis
- Candidate ranking dashboard with shortlist fallback
- Match labels: `Strong Match`, `Moderate Match`, `Weak Match`
- Optional Groq-powered AI review
- CSV export for analysis results

## Tech Stack
- Python
- Streamlit
- scikit-learn
- PyPDF2
- pandas
- plotly
- nltk
- groq

## Project Files
- [app.py](/C:/Users/91849/Desktop/SmartResumeMatcher_Submission/app.py): Streamlit UI and analysis flow
- [utils.py](/C:/Users/91849/Desktop/SmartResumeMatcher_Submission/utils.py): text extraction, similarity, skill logic, AI review helpers
- [requirements.txt](/C:/Users/91849/Desktop/SmartResumeMatcher_Submission/requirements.txt): Python dependencies
- [PROJECT_REPORT.md](/C:/Users/91849/Desktop/SmartResumeMatcher_Submission/PROJECT_REPORT.md): project summary/report
- [VIVA_SCRIPT.md](/C:/Users/91849/Desktop/SmartResumeMatcher_Submission/VIVA_SCRIPT.md): viva preparation notes
- [sample_job_description.txt](/C:/Users/91849/Desktop/SmartResumeMatcher_Submission/sample_job_description.txt): demo JD
- [resume_template_1.txt](/C:/Users/91849/Desktop/SmartResumeMatcher_Submission/resume_template_1.txt): strong match sample
- [resume_template_2.txt](/C:/Users/91849/Desktop/SmartResumeMatcher_Submission/resume_template_2.txt): medium match sample
- [resume_template_3.txt](/C:/Users/91849/Desktop/SmartResumeMatcher_Submission/resume_template_3.txt): backend-heavy sample
- [.streamlit/config.toml](/C:/Users/91849/Desktop/SmartResumeMatcher_Submission/.streamlit/config.toml): Streamlit theme configuration
- [.streamlit/secrets.example.toml](/C:/Users/91849/Desktop/SmartResumeMatcher_Submission/.streamlit/secrets.example.toml): sample secrets file format
- [.gitignore](/C:/Users/91849/Desktop/SmartResumeMatcher_Submission/.gitignore): prevents local secrets and cache files from being submitted

## Setup
1. Open a terminal in `C:\Users\91849\Desktop\SmartResumeMatcher_Submission`
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python streamlit run app.py
```

## Optional AI Review
To enable Groq-based AI review, add your API key in either of these ways:

1. Project secrets file:

```toml
# .streamlit/secrets.toml
GROQ_API_KEY = "your_key_here"
```

2. Environment variable:

```bash
set GROQ_API_KEY=your_key_here
```

If no key is present, the app still works and AI review is simply disabled.
Do not submit your real `secrets.toml`; the repo includes `secrets.example.toml` as a safe template.

## How To Use
1. Paste the job description into the main text box
2. Upload one or more PDF resumes from the sidebar
3. Set the shortlist threshold
4. Click `Analyze resumes`
5. Review the overview, rankings, candidate details, and AI review tabs

## Demo Tips
- Use the provided sample job description and resume templates for testing
- If nobody crosses the threshold, the app automatically promotes the top-scoring candidate as the best available match
- For demo purposes, a threshold around `45-60` usually gives more readable shortlist behavior than a very strict threshold

## Notes
- The app expects resume uploads in PDF format
- Plain `.txt` templates are included for reference and easy copy/paste into your own PDF files
- NLTK-dependent skill extraction now falls back safely if tokenizer data is missing

## Submission Summary
This project demonstrates:
- NLP-based resume screening
- candidate scoring and ranking
- UI design with Streamlit
- optional LLM-assisted evaluation
- practical shortlist support for recruiters
