import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from fpdf import FPDF
import base64
from openai import OpenAI
import tempfile
import numpy as np

# --- API Key Setup ---
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

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

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": ai_prompt}]
    )

    ai_text = response.choices[0].message.content
    return ai_text


# --- Helper Function: Generate Charts ---
def generate_charts(df):
    chart_images = []
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    for col in numeric_cols[:3]:  # limit to 3 charts for simplicity
        fig, ax = plt.subplots()
        df[col].plot(kind="hist", ax=ax, title=f"Distribution of {col}")
        ax.set_xlabel(col)
        buf = BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight")
        buf.seek(0)
        chart_images.append(buf)
        plt.close(fig)
    return chart_images


# --- ✅ Fixed PDF Generation Function ---
def generate_pdf_report(insights_text, chart_images, department, ai_text=""):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, txt=f"{department} AI Report", ln=True, align="C")
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, txt=insights_text)

    if ai_text:
        pdf.add_page()
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, txt="AI Summary", ln=True)
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, txt=ai_text)

    # ✅ Save charts as temp files
    for i, img_buf in enumerate(chart_images):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            tmp.write(img_buf.getbuffer())
            tmp.flush()
            pdf.add_page()
            pdf.image(tmp.name, x=10, y=30, w=180)

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
                    st.image(chart.getvalue())

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
