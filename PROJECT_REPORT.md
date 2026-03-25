# Smart Resume Matcher - Project Report

## 1. Introduction
The **Smart Resume Matcher** is an AI-powered tool designed to automate the initial screening process of recruitment. It uses Natural Language Processing (NLP) techniques to compare resumes against job descriptions and provides a relevance score, helping HR professionals shortlist candidates efficiently.

## 2. Features
- **PDF Parsing**: Extracts text from PDF resumes using `PyPDF2`.
- **Text Preprocessing**: Cleans text by removing stopwords and special characters using `nltk`.
- **Match Score Calculation**: Uses **TF-IDF Vectorization** and **Cosine Similarity** to compute how well a resume matches a job description.
- **Smart Dashboard**:
    - **Sidebar Controls**: Uploads and settings managed in a dedicated sidebar.
    - **Tabbed Results**: Organized views for Overview, Rankings, and Details.
    - **Visual Feedback**: Glassmorphism KPI cards and reduced-clutter layout.
- **Missing Skills Identification**: Highlights key skills from the job description that are missing in the resume.
- **Ranked Results**: Automatically ranks candidates based on their match score.
- **🤖 AI Expert Insights**:
    - **Hiring Recommendation**: AI analyzes the resume to give a "Ready to Hire" or "Not Ready" verdict.
    - **ATS Friendliness Check**: Evaluates if the resume is optimized for Applicant Tracking Systems.
    - **Qualitative Analysis**: Provides strengths, weaknesses, and a detailed summary using the **Llama 3** model via **Groq API**.


## 3. Technology Stack
- **Frontend**: Streamlit (Python framework for data apps)
- **Backend Logic**: Python
- **NLP & ML Libraries**: 
    - `scikit-learn` (TF-IDF, Cosine Similarity)
    - `nltk` (Tokenization, Stopwords)
    - `PyPDF2` (PDF handling)
- **AI Integration**:
    - **Groq API**: High-speed inference engine.
    - **Llama 3.1 (8B)**: Large Language Model for qualitative analysis.



## 4. Key Concepts & Algorithms

### TF-IDF (Term Frequency-Inverse Document Frequency)
TF-IDF is a statistical measure used to evaluate the importance of a word in a document relative to a collection of documents.
- **TF**: How frequently a word appears in a document.
- **IDF**: Reduces the weight of common words (like "the", "and") and increases the weight of rare words (like "Python", "Machine Learning").

### Cosine Similarity
Cosine similarity measures the cosine of the angle between two non-zero vectors in a multi-dimensional space.
- In our case, the Job Description and Resume are converted into vectors.
- A value of **1** (angle 0°) means they are identical.
- A value of **0** (angle 90°) means they are completely different.
- We multiply this by 100 to get a percentage score.

## 5. Project Workflow
1. **Input**: User pastes the **Job Description** in the main area.
2. **Upload**: User uploads PDF resumes via the **Sidebar**.
3. **Extraction**: Text is extracted from the PDFs using `PyPDF2`.
4. **Preprocessing**: Text is cleaned (lowercased, stopwords removed).
5. **Vectorization & Comparison**: TF-IDF and Cosine Similarity calculate the match percentage.
6. **Output**: Results are displayed in an **interactive dashboard** with tabs for *Overview*, *Rankings*, and *Detailed Analysis*.

## 6. Viva Questions & Answers

**Q1: Why did you choose TF-IDF over CountVectorizer?**
*A1: CountVectorizer only counts word frequencies, which can give too much weight to common words. TF-IDF downweights common words and highlights unique, important terms relevant to the job description.*

**Q2: How does Cosine Similarity work?**
*A2: It measures the angle between two text vectors. If the angle is small, the documents are similar. It is preferred over Euclidean distance for text because it focuses on the orientation (content overlap) rather than magnitude (length of document).*

**Q3: What are the limitations of this project?**
*A3: It relies on keyword matching. It doesn't understand context or synonyms (e.g., "AI" vs "Artificial Intelligence" might be treated differently without advanced lemmatization or embeddings like Word2Vec/BERT).*

**Q4: How can you improve this project?**
*A4: We could use pre-trained models like BERT for semantic matching, add a proper database to store candidate profiles, or implement Named Entity Recognition (NER) to extract specific entities like Name, Email, and Education.*
