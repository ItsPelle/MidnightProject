import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
from fpdf import FPDF
import openai
import os

# --- API Key Setup ---
openai.api_key = st.secrets["OPENAI_API_KEY"]

# --- Streamlit App Configuration ---
st.set_page_config(page_title="AI Department Data Analyzer", layout="wide")

st.title("📊 AI Department Data Analyzer")
st.markdown("Upload your department data and generate AI-powered insights + exportable reports.")

# --- File Upload ---
uploaded_file = st.file_uploader("Upload your CSV data file", type=["csv"])

# --- Select Department ---
department = st.selectbox("Select Department", ["Finance", "HR", "Sales", "IT", "Operations", "Marketing"])

# --- Helper Function: Basic AI Data Insights ---
def generate_ai_insights(df, department):
    desc = df.describe(include="all")
    summary = desc.to_markdown()

    ai_prompt = f"""
    You are an AI data analyst for the {department} department.
    Here is a summary of the dataset:

    {summary}

    Please provide detailed analysis and insights for this department. 
    Mention trends, anomalies, and potential recommendations.
    """

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": ai_prompt}]
    )

    ai_text = response.choices[0].message.content
    return ai_text


# --- Helper Function: Generate Charts ---
def generate_charts(df):
    charts = []
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    for col in numeric_cols[:3]:  # limit to 3 charts for simplicity
        fig, ax = plt.subplots()
        df[col].plot(kind="hist", ax=ax, title=f"Distribution of {col}")
        ax.set_xlabel(col)
        buf = BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight")
        buf.seek(0)
        charts.append(fig)
    return charts


# --- Helper Function: Export PDF Report ---
def generate_pdf_report(insights_text, charts, department, ai_text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, txt=f"{department} Department Analysis Report", ln=True, align="C")

    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, txt="AI Insights Summary:\n\n" + insights_text)
    pdf.ln(5)
    pdf.multi_cell(0, 10, txt="AI Data Analysis:\n\n" + ai_text)

    # Add charts properly with file names
    if charts:
        for i, chart in enumerate(charts):
            img_buf = BytesIO()
            chart.savefig(img_buf, format="png", bbox_inches="tight")
            img_buf.seek(0)
            img_filename = f"chart_{i}.png"
            with open(img_filename, "wb") as f:
                f.write(img_buf.getvalue())
            pdf.add_page()
            pdf.image(img_filename, x=10, y=30, w=180)

    pdf_output = BytesIO()
    pdf.output(pdf_output)
    pdf_output.seek(0)
    return pdf_output


# --- Main Logic ---
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.success("✅ File uploaded successfully!")
    st.dataframe(df.head())

    if st.button("Generate AI Insights"):
        with st.spinner("Analyzing data using AI..."):
            try:
                ai_text = generate_ai_insights(df, department)
                st.subheader("🤖 AI Insights")
                st.write(ai_text)

                charts = generate_charts(df)
                for chart in charts:
                    st.pyplot(chart)

                st.session_state["ai_text"] = ai_text
                st.session_state["charts"] = charts

            except Exception as e:
                st.error(f"Error generating AI insights: {e}")

    # --- Export Options ---
    if "ai_text" in st.session_state:
        if st.button("📄 Export Full Report as PDF"):
            insights_text = f"{department} Department Data Insights"
            charts = st.session_state.get("charts", [])
            ai_text = st.session_state.get("ai_text", "")

            with st.spinner("Creating your PDF report..."):
                try:
                    pdf_data = generate_pdf_report(insights_text, charts, department, ai_text)
                    st.download_button(
                        label="Download PDF Report",
                        data=pdf_data,
                        file_name=f"{department}_AI_Report.pdf",
                        mime="application/pdf"
                    )
                    st.success("✅ PDF generated successfully!")
                except Exception as e:
                    st.error(f"Error creating PDF: {e}")

else:
    st.info("👆 Please upload a CSV file to begin analysis.")
