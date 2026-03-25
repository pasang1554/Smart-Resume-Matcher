# Deploying to Streamlit Community Cloud

Your project is ready to go live! Follow these steps to deploy it for free so you can share the link with your professors or friends.

## prerequisites
1.  **GitHub Account**: You need one to host your code.
2.  **Streamlit Account**: Sign up at [share.streamlit.io](https://share.streamlit.io/).

## Step 1: Push Code to GitHub
1.  Create a **new repository** on GitHub (e.g., `smart-resume-matcher`).
2.  Upload the following files to the repository:
    *   `app.py`
    *   `utils.py`
    *   `requirements.txt`
    *   `README.md`
    *   `assets/` (folder)
    *   `data/` (folder)

> **Note**: Do NOT look for a "Upload" button if you have Git installed. Run these commands in your terminal:
> ```bash
> git init
> git add .
> git commit -m "Initial commit"
> git branch -M main
> git remote add origin https://github.com/YOUR_USERNAME/smart-resume-matcher.git
> git push -u origin main
> ```

## Step 2: Deploy on Streamlit
1.  Go to [share.streamlit.io](https://share.streamlit.io/).
2.  Click **"New app"**.
3.  Select your GitHub repository (`smart-resume-matcher`).
4.  **Branch**: `main`.
5.  **Main file path**: `app.py`.
6.  Click **"Deploy!"**.

## Step 3: Secrets (Optional but Recommended)
Since we hardcoded the API Key for the demo, it will work out of the box. 

However, for a real production app, you should:
1.  Remove the hardcoded key from `app.py`.
2.  Go to your App Settings on Streamlit -> **Secrets**.
3.  Add:
    ```toml
    GROQ_API_KEY = "gsk_..."
    ```
4.  Update code to read from `st.secrets["GROQ_API_KEY"]`.

## Troubleshooting
*   **"Module not found"**: Ensure all libraries (like `groq`, `streamlit`, `plotly`) are listed in `requirements.txt`.
*   **"App is crashing"**: Check the logs on the bottom right of the Streamlit dashboard.
