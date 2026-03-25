# 🎙️ Smart Resume Matcher - Viva Presentation Script

**Project Title**: Smart Resume Matcher with AI Verification
**Technologies**: Python, Streamlit, NLP (TF-IDF), Groq API (Llama 3)

---

## 👋 Intro (1 Minute)
"Good morning everyone. My project is the **Smart Resume Matcher**, an AI-powered tool designed to automate the initial screening process of recruitment.
The problem with traditional hiring is volume—HR receives hundreds of resumes and manually scanning them is slow and biased. My solution automates this using **Natural Language Processing (NLP)** and **Generative AI**."

## ⚙️ Core Logic (2 Minutes)
"The project has two main evaluation engines:

1.  **Quantitative Analysis (The 'Math' part)**:
    *   We use **TF-IDF Vectorization** to convert resumes and job descriptions into mathematical vectors.
    *   We calculate the **Cosine Similarity** between them. This gives us a raw percentage match score based on keyword overlap.

2.  **Qualitative Analysis (The 'AI' part)**:
    *   After the initial match, we send the top candidates to the **Groq API** running the **Llama 3.1** model.
    *   This acts as an 'Expert AI Recruiter' that reads the resume to understand context, seniority, and soft skills—things that simple keyword matching misses.

    *   It checks for **ATS Friendliness** and gives a final **'Ready to Hire'** recommendation."

## 🚀 Demo Walkthrough (2 Minutes)
"Let me show you the application:
1.  **Input**: I paste a Job Description here.
2.  **Upload**: I upload a batch of PDF resumes.
3.  **Process**: The system extracts text using `PyPDF2` and cleans it using `nltk`.
4.  **Results**:
    *   **Dashboard**: You see a ranked table of candidates.
    *   **AI Insights**: If I click on a candidate in the 'AI Expert Insights' tab, you see a detailed breakdown: Strengths, Weaknesses, and Missing Critical Skills."

## ❓ Probable Questions (Be Prepared!)

**Q: Why use Groq/Llama 3 instead of just OpenAI?**
**A**: "Groq is a high-speed inference engine. For a real-time application like this where a recruiter might upload 50 resumes, we need near-instant analysis. Llama 3 on Groq is incredibly fast and open-source."

**Q: What is TF-IDF?**
**A**: "Term Frequency-Inverse Document Frequency. It highlights words that are unique and important to the Job Description, rather than just counting common words like 'the' or 'and'."

**Q: How accurate is the score?**
**A**: "The TF-IDF score is a good baseline for keyword matching. The AI evaluation adds a layer of semantic understanding, making the final assessment much more reliable than keyword matching alone."

---
*Good luck with your presentation!*
