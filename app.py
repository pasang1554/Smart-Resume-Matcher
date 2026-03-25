import os
from io import BytesIO
from datetime import datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from streamlit.errors import StreamlitSecretNotFoundError

from utils import (
    calculate_similarity,
    calculate_skill_depth,
    detect_bias_indicators,
    evaluate_resume_with_groq,
    extract_semantic_skills,
    extract_text_from_pdf,
    find_missing_skills,
)

try:
    from groq import Groq
except Exception:
    Groq = None

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import inch
    from reportlab.pdfgen import canvas
except Exception:
    A4 = None
    inch = None
    canvas = None


st.set_page_config(
    page_title="Smart Resume Matcher",
    page_icon="R",
    layout="wide",
    initial_sidebar_state="expanded",
)


if "analysis_history" not in st.session_state:
    st.session_state.analysis_history = []


def inject_styles() -> None:
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=Source+Serif+4:wght@600;700&display=swap');
            .stApp {
                background:
                    radial-gradient(circle at top left, rgba(20, 184, 166, 0.10), transparent 26%),
                    radial-gradient(circle at top right, rgba(245, 158, 11, 0.08), transparent 24%),
                    linear-gradient(180deg, #f7f4ee 0%, #f3efe8 100%);
                color: #172033;
            }
            html, body, [class*="css"]  {
                font-family: 'Manrope', sans-serif;
            }
            .block-container {
                padding-top: 1.5rem;
                padding-bottom: 3rem;
                max-width: 1180px;
            }
            [data-testid="stSidebar"] {
                background: linear-gradient(180deg, #182235 0%, #101827 100%);
                border-right: 1px solid rgba(148, 163, 184, 0.10);
            }
            [data-testid="stSidebar"] * {
                color: #edf4ff;
            }
            [data-testid="stSidebar"] .stCaption {
                color: #cbd8ee;
            }
            [data-testid="stSidebar"] .stSuccess,
            [data-testid="stSidebar"] .stInfo {
                color: inherit;
            }
            [data-testid="stSidebar"] [data-testid="stFileUploader"] section {
                background: rgba(255, 255, 255, 0.06) !important;
                border: 1px dashed rgba(148, 163, 184, 0.28) !important;
                border-radius: 18px !important;
            }
            [data-testid="stSidebar"] [data-testid="stFileUploader"] section:hover {
                border-color: rgba(45, 212, 191, 0.45) !important;
                background: rgba(255, 255, 255, 0.08) !important;
            }
            [data-testid="stSidebar"] [data-testid="stFileUploader"] small,
            [data-testid="stSidebar"] [data-testid="stFileUploader"] span,
            [data-testid="stSidebar"] [data-testid="stFileUploader"] p {
                color: #dbe7f8 !important;
            }
            [data-testid="stSidebar"] [data-testid="stFileUploader"] button {
                background: rgba(255, 255, 255, 0.08) !important;
                color: #edf4ff !important;
                border: 1px solid rgba(148, 163, 184, 0.22) !important;
                box-shadow: none !important;
            }
            [data-testid="stSidebar"] [data-testid="stFileUploader"] button:hover {
                background: rgba(255, 255, 255, 0.12) !important;
                border-color: rgba(45, 212, 191, 0.40) !important;
            }
            [data-testid="stSidebar"] [data-baseweb="slider"] > div {
                color: #14b8a6;
            }
            .stTextArea textarea,
            .stTextInput input {
                border-radius: 18px !important;
                border: 1px solid rgba(148, 163, 184, 0.28) !important;
                background: rgba(255, 255, 255, 0.72) !important;
                color: #172033 !important;
                line-height: 1.65 !important;
            }
            .stTextArea textarea:focus,
            .stTextInput input:focus {
                border-color: rgba(20, 184, 166, 0.55) !important;
                box-shadow: 0 0 0 1px rgba(20, 184, 166, 0.22) !important;
            }
            .stButton > button,
            .stDownloadButton > button {
                border-radius: 14px !important;
                border: none !important;
                background: linear-gradient(135deg, #0f766e 0%, #0f766e 45%, #155e75 100%) !important;
                color: #ffffff !important;
                font-weight: 700 !important;
                letter-spacing: 0.01em;
                padding: 0.72rem 1rem !important;
                box-shadow: 0 14px 30px rgba(15, 118, 110, 0.18);
            }
            .stButton > button:hover,
            .stDownloadButton > button:hover {
                background: linear-gradient(135deg, #115e59 0%, #0f766e 100%) !important;
                transform: translateY(-1px);
            }
            .stTabs [data-baseweb="tab-list"] {
                gap: 0.4rem;
                background: rgba(255,255,255,0.48);
                border: 1px solid rgba(148, 163, 184, 0.16);
                padding: 0.35rem;
                border-radius: 16px;
            }
            .stTabs [data-baseweb="tab"] {
                border-radius: 12px;
                padding: 0.55rem 0.95rem;
                color: #516074;
                font-weight: 700;
            }
            .stTabs [aria-selected="true"] {
                background: #ffffff !important;
                color: #172033 !important;
                box-shadow: 0 6px 18px rgba(15, 23, 42, 0.08);
            }
            .stExpander {
                border: 1px solid rgba(148, 163, 184, 0.16) !important;
                border-radius: 18px !important;
                background: rgba(255,255,255,0.75);
            }
            .hero-card,
            .panel-card,
            .stat-card {
                background: rgba(255, 252, 248, 0.84);
                border: 1px solid rgba(125, 138, 160, 0.14);
                border-radius: 24px;
                box-shadow: 0 18px 45px rgba(33, 44, 68, 0.06);
                backdrop-filter: blur(10px);
            }
            .hero-card {
                padding: 2.25rem;
                margin-bottom: 1.2rem;
            }
            .hero-kicker {
                color: #0f766e;
                font-size: 0.78rem;
                font-weight: 700;
                letter-spacing: 0.14em;
                text-transform: uppercase;
                margin-bottom: 0.8rem;
            }
            .hero-title {
                color: #172033;
                font-family: 'Source Serif 4', serif;
                font-size: 3.3rem;
                font-weight: 700;
                line-height: 1.02;
                letter-spacing: -0.03em;
                margin-bottom: 0.8rem;
            }
            .hero-copy {
                color: #526074;
                font-size: 1.03rem;
                max-width: 660px;
                margin-bottom: 0;
            }
            .panel-card {
                padding: 1.15rem 1.2rem 0.55rem 1.2rem;
                margin-bottom: 1rem;
            }
            .panel-card.soft {
                background: linear-gradient(135deg, rgba(255, 252, 248, 0.92), rgba(245, 248, 250, 0.92));
            }
            .section-title {
                color: #172033;
                font-size: 1.08rem;
                font-weight: 700;
                margin-bottom: 0.35rem;
            }
            .section-copy {
                color: #617084;
                font-size: 0.95rem;
                margin-bottom: 1rem;
            }
            .stat-card {
                padding: 1.1rem 1.2rem;
            }
            .stat-label {
                color: #64748b;
                font-size: 0.8rem;
                font-weight: 700;
                letter-spacing: 0.06em;
                text-transform: uppercase;
            }
            .stat-value {
                color: #172033;
                font-size: 2rem;
                font-weight: 800;
                line-height: 1.1;
                margin-top: 0.35rem;
            }
            .chip-row {
                display: flex;
                flex-wrap: wrap;
                gap: 0.45rem;
                margin: 0.5rem 0 0.25rem 0;
            }
            .chip {
                display: inline-block;
                padding: 0.35rem 0.7rem;
                border-radius: 999px;
                background: #dff5f0;
                color: #0f5f5a;
                font-size: 0.82rem;
                font-weight: 600;
            }
            .chip.warn {
                background: #fbe4dd;
                color: #a33c21;
            }
            .candidate-card {
                border: 1px solid rgba(125, 138, 160, 0.15);
                border-radius: 22px;
                background: rgba(255, 252, 248, 0.84);
                padding: 1rem 1rem 0.2rem 1rem;
                margin-bottom: 0.9rem;
            }
            .candidate-card.shortlisted {
                border: 2px solid rgba(15, 118, 110, 0.24);
                background: linear-gradient(135deg, rgba(244, 251, 248, 0.98), rgba(255, 252, 248, 0.94));
                box-shadow: 0 18px 40px rgba(15, 118, 110, 0.10);
            }
            .candidate-header {
                display: flex;
                justify-content: space-between;
                gap: 1rem;
                align-items: center;
                margin-bottom: 0.8rem;
            }
            .candidate-name {
                color: #172033;
                font-size: 1.05rem;
                font-weight: 700;
            }
            .candidate-score {
                color: #0f766e;
                font-size: 1.25rem;
                font-weight: 800;
            }
            .status-pill {
                display: inline-block;
                padding: 0.35rem 0.7rem;
                border-radius: 999px;
                font-size: 0.78rem;
                font-weight: 700;
                letter-spacing: 0.03em;
                margin-top: 0.35rem;
            }
            .status-pill.shortlisted {
                background: #dcfce7;
                color: #166534;
            }
            .status-pill.review {
                background: #ffedd5;
                color: #9a3412;
            }
            .top-pick-banner {
                margin: 1rem 0 1.2rem 0;
                padding: 1.2rem 1.2rem;
                border-radius: 22px;
                background: linear-gradient(135deg, #17324d 0%, #0f766e 100%);
                color: white;
                box-shadow: 0 18px 40px rgba(23, 50, 77, 0.18);
            }
            .top-pick-label {
                font-size: 0.78rem;
                font-weight: 700;
                letter-spacing: 0.08em;
                text-transform: uppercase;
                opacity: 0.9;
            }
            .top-pick-name {
                font-size: 1.5rem;
                font-weight: 800;
                margin: 0.3rem 0 0.2rem 0;
            }
            .top-pick-copy {
                font-size: 0.98rem;
                opacity: 0.96;
                margin: 0;
            }
            .footer-note {
                color: #617084;
                text-align: center;
                margin-top: 2rem;
                font-size: 0.9rem;
            }
            .mini-note {
                color: #617084;
                font-size: 0.88rem;
                margin-top: 0.35rem;
            }
            .sidebar-card {
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(148, 163, 184, 0.12);
                border-radius: 18px;
                padding: 0.9rem 1rem;
                margin: 0.75rem 0 1rem 0;
            }
            .sidebar-title {
                font-size: 0.8rem;
                text-transform: uppercase;
                letter-spacing: 0.08em;
                font-weight: 700;
                color: #8ee4d7;
                margin-bottom: 0.35rem;
            }
            .sidebar-copy {
                font-size: 0.92rem;
                color: #dde7f7;
                margin: 0;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def get_groq_api_key() -> str | None:
    try:
        if "GROQ_API_KEY" in st.secrets:
            return st.secrets["GROQ_API_KEY"]
    except StreamlitSecretNotFoundError:
        pass
    return os.getenv("GROQ_API_KEY")


def format_skill_chips(skills: list[str], warn: bool = False) -> str:
    if not skills:
        return "<span class='section-copy'>No skills detected.</span>"
    chip_class = "chip warn" if warn else "chip"
    return "<div class='chip-row'>" + "".join(
        f"<span class='{chip_class}'>{skill}</span>" for skill in skills
    ) + "</div>"


def safe_extract_resume_text(file) -> str:
    text = extract_text_from_pdf(file) or ""
    try:
        file.seek(0)
    except Exception:
        pass
    return text


def build_top_candidate_summary(row: dict) -> list[str]:
    strengths = ", ".join(row["Matched Skills"][:4]) if row["Matched Skills"] else "general resume relevance"
    gaps = ", ".join(row["Missing Skills"][:3]) if row["Missing Skills"] else "no major skill gaps detected"
    return [
        f"{row['Candidate']} is the current top recommendation with a {row['Match Score']}% overall match.",
        f"Best signals: {strengths}.",
        f"Main gaps: {gaps}.",
    ]


def generate_pdf_report(job_description: str, df: pd.DataFrame) -> bytes | None:
    if canvas is None or A4 is None or inch is None:
        return None

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 0.75 * inch

    def write_line(text: str, font: str = "Helvetica", size: int = 10, indent: float = 0) -> None:
        nonlocal y
        pdf.setFont(font, size)
        max_chars = 95
        remaining = text.strip()
        while remaining:
            chunk = remaining[:max_chars]
            if len(remaining) > max_chars:
                split_at = chunk.rfind(" ")
                if split_at > 20:
                    chunk = chunk[:split_at]
            pdf.drawString(0.75 * inch + indent, y, chunk)
            y -= 0.22 * inch
            remaining = remaining[len(chunk):].strip()
            if y < 0.8 * inch:
                pdf.showPage()
                y = height - 0.75 * inch

    pdf.setTitle("Smart Resume Matcher Report")
    write_line("Smart Resume Matcher Report", "Helvetica-Bold", 16)
    write_line(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", size=9)
    write_line("")
    write_line("Job Description Preview", "Helvetica-Bold", 12)
    write_line(job_description[:700] or "No job description provided.")
    write_line("")
    write_line("Candidate Rankings", "Helvetica-Bold", 12)

    for row in df.to_dict("records"):
        write_line(
            f"#{row['Rank']} {row['Candidate']} | {row['Match Score']}% | {row['Status']} | {row['Match Band']}",
            "Helvetica-Bold",
            10,
        )
        write_line(
            f"Semantic: {row['Semantic Similarity']}% | Skill overlap: {row['Skill Overlap']}% | Skill depth: {row['Skill Depth']}",
            size=9,
            indent=10,
        )
        write_line(
            f"Matched skills: {', '.join(row['Matched Skills'][:6]) if row['Matched Skills'] else 'None'}",
            size=9,
            indent=10,
        )
        write_line(
            f"Missing skills: {', '.join(row['Missing Skills'][:6]) if row['Missing Skills'] else 'None'}",
            size=9,
            indent=10,
        )
        write_line("")

    pdf.save()
    return buffer.getvalue()


def analyze_resume(
    job_description: str,
    file,
    threshold: int,
    enable_bias_check: bool,
    enable_ai_review: bool,
    groq_api_key: str | None,
) -> dict | None:
    resume_text = safe_extract_resume_text(file)
    if not resume_text or len(resume_text.strip()) < 50:
        return None

    similarity_score = calculate_similarity(job_description, resume_text)
    required_skills = extract_semantic_skills(job_description)
    candidate_skills = extract_semantic_skills(resume_text)
    missing_skills = find_missing_skills(job_description, resume_text)
    skill_depth = calculate_skill_depth(resume_text, candidate_skills[:8])
    bias_flags = detect_bias_indicators(resume_text) if enable_bias_check else []

    overlap_ratio = (
        (len(set(required_skills) & set(candidate_skills)) / len(required_skills)) * 100
        if required_skills
        else 0
    )
    depth_bonus = min(skill_depth * 2, 10)
    penalty = min(len(bias_flags) * 2, 8)

    # Blend document similarity with direct skill overlap so realistic resumes
    # are not under-scored when wording differs from the job description.
    weighted_score = (similarity_score * 0.45) + (overlap_ratio * 0.45) + (depth_bonus * 1.0)
    final_score = max(0, min(100, weighted_score - penalty))
    if final_score >= max(threshold + 10, 80):
        match_band = "Strong Match"
    elif final_score >= threshold:
        match_band = "Moderate Match"
    else:
        match_band = "Weak Match"

    status = "Shortlisted" if final_score >= threshold else "Needs Review"

    ai_evaluation = None
    if enable_ai_review and groq_api_key and Groq is not None:
        try:
            client = Groq(api_key=groq_api_key)
            ai_evaluation = evaluate_resume_with_groq(client, job_description, resume_text)
        except Exception as exc:
            ai_evaluation = {"error": str(exc)}

    return {
        "Rank": 0,
        "Candidate": file.name.replace(".pdf", ""),
        "Match Score": round(final_score, 1),
        "Semantic Similarity": round(similarity_score, 1),
        "Skill Overlap": round(overlap_ratio, 1),
        "Skill Depth": round(skill_depth, 1),
        "Match Band": match_band,
        "Matched Skills": candidate_skills,
        "Matched Skill Count": len(candidate_skills),
        "Missing Skills": missing_skills,
        "Missing Count": len(missing_skills),
        "Bias Flags": bias_flags,
        "Bias Count": len(bias_flags),
        "Status": status,
        "Fallback Shortlist": False,
        "Processed At": datetime.now().strftime("%H:%M:%S"),
        "AI Review": ai_evaluation,
    }


def apply_shortlist_fallback(results: list[dict], threshold: int) -> list[dict]:
    if not results:
        return results

    shortlisted = [item for item in results if item["Match Score"] >= threshold]
    if shortlisted:
        return results

    best_index = max(range(len(results)), key=lambda idx: results[idx]["Match Score"])
    results[best_index]["Status"] = "Shortlisted"
    if results[best_index]["Match Band"] == "Weak Match":
        results[best_index]["Match Band"] = "Moderate Match"
    results[best_index]["Fallback Shortlist"] = True

    for idx, item in enumerate(results):
        if idx != best_index:
            item["Fallback Shortlist"] = False

    return results


def render_header() -> None:
    st.markdown(
        """
        <div class="hero-card">
            <div class="hero-kicker">Hiring Desk</div>
            <div class="hero-title">Review resumes with a cleaner shortlist workflow.</div>
            <p class="hero-copy">
                Paste a role brief, upload candidate resumes, and get a ranked view that is easier to read,
                easier to explain, and better suited for a live project demo.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_overview(df: pd.DataFrame, threshold: int) -> None:
    total_candidates = len(df)
    shortlisted = int((df["Status"] == "Shortlisted").sum())
    avg_score = float(df["Match Score"].mean()) if total_candidates else 0.0
    top_score = float(df["Match Score"].max()) if total_candidates else 0.0

    cols = st.columns(4)
    stats = [
        ("Candidates", total_candidates),
        ("Shortlisted", shortlisted),
        ("Average Score", f"{avg_score:.1f}%"),
        ("Top Score", f"{top_score:.1f}%"),
    ]
    for col, (label, value) in zip(cols, stats):
        with col:
            st.markdown(
                f"""
                <div class="stat-card">
                    <div class="stat-label">{label}</div>
                    <div class="stat-value">{value}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        fig = px.bar(
            df,
            x="Candidate",
            y="Match Score",
            color="Status",
            color_discrete_map={"Shortlisted": "#0f766e", "Needs Review": "#ea580c"},
        )
        fig.add_hline(y=threshold, line_dash="dash", line_color="#b91c1c")
        fig.update_layout(
            height=360,
            showlegend=True,
            margin=dict(l=10, r=10, t=20, b=10),
            xaxis_title="Candidate",
            yaxis_title="Score",
            paper_bgcolor="rgba(255,255,255,0)",
            plot_bgcolor="rgba(255,255,255,0)",
            legend_title="Review Status",
            font=dict(color="#334155"),
        )
        fig.update_xaxes(showgrid=False, tickangle=-15)
        fig.update_yaxes(showgrid=True, gridcolor="rgba(148, 163, 184, 0.2)")
        st.plotly_chart(fig, use_container_width=True)

    with chart_col2:
        fig = go.Figure(
            go.Pie(
                labels=["Shortlisted", "Needs Review"],
                values=[shortlisted, max(total_candidates - shortlisted, 0)],
                hole=0.58,
                marker=dict(colors=["#0f766e", "#cbd5e1"]),
            )
        )
        fig.update_layout(
            height=360,
            margin=dict(l=10, r=10, t=20, b=10),
            paper_bgcolor="rgba(255,255,255,0)",
            font=dict(color="#334155"),
            showlegend=True,
            legend_title="Candidate Status",
        )
        st.plotly_chart(fig, use_container_width=True)

    if "Fallback Shortlist" in df.columns and bool(df["Fallback Shortlist"].fillna(False).any()):
        st.info("No one cleared the shortlist threshold, so the strongest available candidate has been surfaced for review.")

    top_candidate = df.iloc[0].to_dict()
    st.markdown(
        "<div class='panel-card soft'><div class='section-title'>Top candidate summary</div><div class='section-copy'>A quick read on why this resume is currently leading the stack.</div></div>",
        unsafe_allow_html=True,
    )
    for line in build_top_candidate_summary(top_candidate):
        st.write(f"- {line}")


def render_rankings(df: pd.DataFrame) -> None:
    top_candidate = df.iloc[0].to_dict()
    fallback_note = ""
    if top_candidate.get("Fallback Shortlist"):
        fallback_note = "No one crossed the threshold, so this resume is being surfaced as the strongest available option."
    elif top_candidate["Status"] == "Shortlisted":
        fallback_note = "This resume leads the shortlist based on the strongest overall match across skills, similarity, and depth."

    if fallback_note:
        st.markdown(
            f"""
            <div class="top-pick-banner">
                <div class="top-pick-label">Lead Candidate</div>
                <div class="top-pick-name">{top_candidate["Candidate"]} | {top_candidate["Match Score"]}%</div>
                <p class="top-pick-copy">{fallback_note}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    for row in df.head(5).to_dict("records"):
        card_class = "candidate-card shortlisted" if row["Status"] == "Shortlisted" else "candidate-card"
        status_class = "status-pill shortlisted" if row["Status"] == "Shortlisted" else "status-pill review"
        st.markdown(
            f"""
            <div class="{card_class}">
                <div class="candidate-header">
                    <div>
                        <div class="candidate-name">#{row["Rank"]} {row["Candidate"]}</div>
                        <div class="section-copy">Matched skills: {row["Matched Skill Count"]} | Missing skills: {row["Missing Count"]} | {row["Match Band"]}</div>
                    </div>
                    <div style="text-align: right;">
                        <div class="candidate-score">{row["Match Score"]}%</div>
                        <span class="{status_class}">{row["Status"]}</span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.dataframe(
        df[
            [
                "Rank",
                "Candidate",
                "Match Score",
                "Semantic Similarity",
                "Skill Overlap",
                "Skill Depth",
                "Match Band",
                "Matched Skill Count",
                "Missing Count",
                "Status",
            ]
        ],
        column_config={
            "Match Score": st.column_config.ProgressColumn("Match Score", min_value=0, max_value=100, format="%.1f%%"),
            "Semantic Similarity": st.column_config.ProgressColumn("Semantic Similarity", min_value=0, max_value=100, format="%.1f%%"),
            "Skill Overlap": st.column_config.ProgressColumn("Skill Overlap", min_value=0, max_value=100, format="%.1f%%"),
            "Skill Depth": st.column_config.NumberColumn("Skill Depth", format="%.1f"),
        },
        hide_index=True,
        use_container_width=True,
    )


def render_candidate_details(df: pd.DataFrame) -> None:
    for row in df.to_dict("records"):
        with st.expander(f'#{row["Rank"]} {row["Candidate"]} | {row["Match Score"]}%'):
            metric_cols = st.columns(4)
            metric_cols[0].metric("Match Score", f'{row["Match Score"]}%')
            metric_cols[1].metric("Semantic Similarity", f'{row["Semantic Similarity"]}%')
            metric_cols[2].metric("Skill Overlap", f'{row["Skill Overlap"]}%')
            metric_cols[3].metric("Skill Depth", row["Skill Depth"])

            st.caption(f'Bias flags detected: {row["Bias Count"]}')
            st.caption(f'Match level: {row["Match Band"]}')

            if row.get("Fallback Shortlist"):
                st.info("This candidate was promoted for review because no applicant crossed the shortlist threshold.")

            detail_cols = st.columns(2)
            with detail_cols[0]:
                st.markdown(
                    "<div class='section-title'>Matched skills</div>",
                    unsafe_allow_html=True,
                )
                st.markdown(format_skill_chips(row["Matched Skills"][:12]), unsafe_allow_html=True)

            with detail_cols[1]:
                st.markdown(
                    "<div class='section-title'>Missing skills</div>",
                    unsafe_allow_html=True,
                )
                st.markdown(
                    format_skill_chips(row["Missing Skills"][:12], warn=True),
                    unsafe_allow_html=True,
                )

            if row["Bias Flags"]:
                st.warning("Potential bias-related terms found: " + ", ".join(row["Bias Flags"]))


def render_ai_reviews(df: pd.DataFrame, ai_enabled: bool) -> None:
    if not ai_enabled:
        st.info("AI review is currently off. Add a Groq API key in Streamlit secrets or environment variables to enable it.")
        return

    shown = False
    for row in df.to_dict("records"):
        review = row.get("AI Review")
        if not review:
            continue
        shown = True
        with st.expander(f'{row["Candidate"]} AI review'):
            if "error" in review:
                st.error(review["error"])
                continue
            c1, c2, c3 = st.columns(3)
            c1.metric("AI Match Score", review.get("match_score", "N/A"))
            c2.metric("ATS Score", review.get("ats_friendly_score", "N/A"))
            c3.metric("Recommendation", review.get("recommendation", "N/A"))

            st.write(review.get("summary", "No summary available."))
            strengths = review.get("strengths", [])
            weaknesses = review.get("weaknesses", [])
            missing = review.get("missing_critical_skills", [])

            cols = st.columns(3)
            with cols[0]:
                st.markdown("**Strengths**")
                if strengths:
                    for item in strengths:
                        st.write(f"- {item}")
                else:
                    st.caption("No strengths listed.")
            with cols[1]:
                st.markdown("**Weaknesses**")
                if weaknesses:
                    for item in weaknesses:
                        st.write(f"- {item}")
                else:
                    st.caption("No major weaknesses listed.")
            with cols[2]:
                st.markdown("**Missing critical skills**")
                if missing:
                    for item in missing:
                        st.write(f"- {item}")
                else:
                    st.caption("No major critical skill gaps identified.")

    if not shown:
        st.info("No AI review output was returned for this run.")


inject_styles()
render_header()

with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-card">
            <div class="sidebar-title">Resume Review</div>
            <p class="sidebar-copy">Set the hiring bar, upload resumes, and turn a messy stack of PDFs into one clear shortlist.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("## Inputs")
    uploaded_files = st.file_uploader(
        "Upload resume PDFs",
        type=["pdf"],
        accept_multiple_files=True,
        help="Upload one or more resumes in PDF format.",
    )
    threshold = st.slider("Shortlist threshold", min_value=0, max_value=100, value=65)
    enable_bias_check = st.toggle("Bias indicator check", value=True)

    groq_api_key = get_groq_api_key()
    enable_ai_review = st.toggle(
        "AI review",
        value=bool(groq_api_key),
        disabled=not bool(groq_api_key),
        help="Requires GROQ_API_KEY in Streamlit secrets or environment variables.",
    )

    st.markdown("## Session")
    st.caption(f"Runs in this session: {len(st.session_state.analysis_history)}")
    if groq_api_key:
        st.success("Groq key detected.")
    else:
        st.caption("No Groq key found. Core matching still works without AI review.")


st.markdown(
    """
    <div class="panel-card soft">
        <div class="section-title">Role brief</div>
        <div class="section-copy">Paste the job description here. The app will use it as the baseline for scoring, skill matching, and shortlist decisions.</div>
    </div>
    """,
    unsafe_allow_html=True,
)
job_description = st.text_area(
    "Job description",
    height=220,
    label_visibility="collapsed",
    placeholder="Paste the job description, required skills, experience expectations, and qualifications here.",
)

if job_description.strip():
    required_skills = extract_semantic_skills(job_description)
    if required_skills:
        st.markdown(
            "<div class='panel-card soft'><div class='section-title'>What the role seems to prioritize</div>"
            + format_skill_chips(required_skills[:14])
            + "<div class='mini-note'>These terms are pulled from the role brief and used as the main comparison signals.</div>"
            + "</div>",
            unsafe_allow_html=True,
        )

if uploaded_files:
    with st.expander("Resume Preview", expanded=False):
        st.caption("Open this first if you want to check whether the PDF text was extracted properly.")
        for file in uploaded_files:
            preview_text = safe_extract_resume_text(file)
            st.markdown(f"**{file.name}**")
            if preview_text.strip():
                st.text_area(
                    f"Preview for {file.name}",
                    value=preview_text[:900],
                    height=140,
                    disabled=True,
                    key=f"preview_{file.name}",
                    label_visibility="collapsed",
                )
            else:
                st.warning(f"Could not extract readable text from {file.name}.")


analyze_clicked = st.button("Analyze resumes", type="primary", use_container_width=True)

if analyze_clicked:
    if not job_description.strip():
        st.error("Please enter a job description before running the analysis.")
    elif not uploaded_files:
        st.error("Please upload at least one PDF resume.")
    else:
        results = []
        progress = st.progress(0, text="Starting resume analysis...")

        for index, file in enumerate(uploaded_files, start=1):
            progress.progress(
                index / len(uploaded_files),
                text=f"Analyzing {file.name} ({index}/{len(uploaded_files)})",
            )
            result = analyze_resume(
                job_description=job_description,
                file=file,
                threshold=threshold,
                enable_bias_check=enable_bias_check,
                enable_ai_review=enable_ai_review,
                groq_api_key=groq_api_key,
            )
            if result:
                results.append(result)

        progress.empty()

        if not results:
            st.error("No valid resume text could be extracted from the uploaded PDFs.")
        else:
            results = sorted(results, key=lambda item: item["Match Score"], reverse=True)
            results = apply_shortlist_fallback(results, threshold)
            for index, row in enumerate(results, start=1):
                row["Rank"] = index

            df = pd.DataFrame(results)
            st.session_state.analysis_history.append(
                {
                    "timestamp": datetime.now(),
                    "job_preview": job_description[:80],
                    "count": len(df),
                }
            )

            tabs = st.tabs(["Overview", "Rankings", "Candidate Details", "AI Review"])
            with tabs[0]:
                render_overview(df, threshold)
            with tabs[1]:
                render_rankings(df)
                csv_data = df.to_csv(index=False).encode("utf-8")
                pdf_data = generate_pdf_report(job_description, df)
                st.download_button(
                    "Download CSV",
                    data=csv_data,
                    file_name=f"resume_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                )
                if pdf_data:
                    st.download_button(
                        "Download PDF Report",
                        data=pdf_data,
                        file_name=f"resume_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                        mime="application/pdf",
                    )
                else:
                    st.caption("PDF export requires the `reportlab` package.")
            with tabs[2]:
                render_candidate_details(df)
            with tabs[3]:
                render_ai_reviews(df, enable_ai_review)


st.markdown(
    """
    <div class="footer-note">
        Smart Resume Matcher uses TF-IDF similarity, skill extraction, and optional AI review to support shortlist decisions.
    </div>
    """,
    unsafe_allow_html=True,
)
