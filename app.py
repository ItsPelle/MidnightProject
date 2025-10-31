import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from fpdf import FPDF
import base64

st.set_page_config(page_title="AI Business Insights System", layout="wide")

# Sidebar logo + navigation
st.sidebar.image("https://i.imgur.com/vy7RaWQ.png", width=180)
st.sidebar.title("Department Navigation")
department = st.sidebar.selectbox(
    "Select Department",
    ["Overview", "Finance", "Marketing", "HR", "Membership"]
)

st.title("🤖 AI Organizational Insights System")
st.write("Upload department reports (CSV) and get AI-powered summaries, visualizations, and downloadable reports.")


# -------------------- CORE AI ANALYSIS LOGIC --------------------
def generate_ai_insights(df, department):
    insights = ""

    if df.empty:
        return "⚠️ No data found in the uploaded file."

    insights += f"### 📊 Data Overview\n"
    insights += f"- Rows: {df.shape[0]}\n"
    insights += f"- Columns: {df.shape[1]}\n\n"

    numeric_cols = df.select_dtypes(include=['number']).columns
    text_cols = df.select_dtypes(include=['object']).columns

    if len(numeric_cols) > 0:
        desc = df[numeric_cols].describe().T
        insights += "### 🔢 Numeric Summary\n"
        insights += desc.to_markdown() + "\n\n"

    if len(text_cols) > 0:
        insights += "### 🗂️ Common Text Fields\n"
        for col in text_cols:
            most_common = df[col].mode()[0] if not df[col].mode().empty else "N/A"
            insights += f"- **{col}:** Most common → {most_common}\n"
        insights += "\n"

    # -------------------- Department-Specific Recommendations --------------------
    insights += "## 💡 AI Recommendations\n"

    if department == "Finance":
        insights += "- 💰 Review budget allocation for cost efficiency.\n"
        insights += "- 📈 Automate expense tracking to reduce errors.\n"
        if any("expense" in c.lower() for c in df.columns):
            avg_exp = df[[c for c in df.columns if "expense" in c.lower()]].mean().mean()
            if avg_exp > 500000:
                insights += "- ⚠️ High expenses detected. Consider reducing non-essential spending.\n"
            else:
                insights += "- ✅ Spending appears within a healthy range.\n"

    elif department == "Marketing":
        insights += "- 📢 Focus on high-performing campaigns.\n"
        insights += "- 📊 Consider A/B testing new ad creatives.\n"
        if any("leads" in c.lower() for c in df.columns):
            avg_leads = df[[c for c in df.columns if "leads" in c.lower()]].mean().mean()
            insights += f"- Average leads: **{avg_leads:.1f}**\n"

    elif department == "HR":
        insights += "- 👥 Monitor attendance and engagement metrics.\n"
        insights += "- 🧠 Invest in training for low-performing teams.\n"

    elif department == "Membership":
        insights += "- 🎯 Track new vs returning members.\n"
        insights += "- 📉 If growth slows, offer loyalty rewards.\n"
        if any("member" in c.lower() for c in df.columns):
            total_members = df[[c for c in df.columns if "member" in c.lower()]].sum().sum()
            insights += f"- Total membership count: **{total_members:,.0f}**\n"

    else:
        insights += "- 📘 Upload department data for deeper insights.\n"

    return insights


# -------------------- VISUALIZATION FUNCTION --------------------
def show_charts(df):
    numeric_cols = df.select_dtypes(include=['number']).columns

    if len(numeric_cols) == 0:
        st.info("No numeric columns found for visualization.")
        return None

    st.subheader("📉 Data Visualizations")
    images = []

    # Bar Chart
    st.markdown("#### Average by Column")
    mean_values = df[numeric_cols].mean().sort_values(ascending=False)
    fig, ax = plt.subplots()
    mean_values.plot(kind="bar", ax=ax)
    st.pyplot(fig)
    buf = BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    images.append(buf)

    # Pie Chart
    st.markdown("#### Value Distribution (Pie Chart)")
    first_col = numeric_cols[0]
    fig2, ax2 = plt.subplots()
    df[first_col].value_counts().head(5).plot(kind='pie', autopct='%1.1f%%', ax=ax2)
    ax2.set_ylabel('')
    st.pyplot(fig2)
    buf2 = BytesIO()
    fig2.savefig(buf2, format="png")
    buf2.seek(0)
    images.append(buf2)

    # Trend Chart
    date_cols = [c for c in df.columns if 'date' in c.lower() or 'time' in c.lower()]
    if len(date_cols) > 0:
        st.markdown("#### Trend Over Time")
        try:
            df[date_cols[0]] = pd.to_datetime(df[date_cols[0]], errors='coerce')
            trend_df = df.groupby(df[date_cols[0]].dt.to_period("M"))[numeric_cols[0]].mean()
            fig3, ax3 = plt.subplots()
            trend_df.plot(kind="line", ax=ax3, marker='o')
            st.pyplot(fig3)
            buf3 = BytesIO()
            fig3.savefig(buf3, format="png")
            buf3.seek(0)
            images.append(buf3)
        except:
            st.warning("⚠️ Couldn't process trend chart — check your date column format.")
    return images


# -------------------- FIXED PDF REPORT GENERATOR --------------------
def generate_pdf_report(insights_text, chart_images, department):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, txt=f"{department} AI Report", ln=True, align="C")
    pdf.set_font("Arial", size=12)

    # Fix encoding for emojis/unicode
    safe_text = insights_text.encode("latin-1", "replace").decode("latin-1")
    pdf.multi_cell(0, 10, txt=safe_text)

    for img_buf in chart_images:
        pdf.add_page()
        pdf.image(img_buf, x=10, y=30, w=180)

    pdf_output = BytesIO()
    pdf.output(pdf_output)
    pdf_output.seek(0)
    return pdf_output


# -------------------- FILE UPLOAD + DISPLAY --------------------
sample_csv = """name,expense,leads,date
Campaign A,400000,120,2024-01-01
Campaign B,600000,90,2024-02-01
Campaign C,550000,130,2024-03-01
"""
st.download_button(
    label="⬇️ Download Sample CSV (for testing)",
    data=sample_csv,
    file_name="sample_data.csv",
    mime="text/csv"
)

uploaded_file = st.file_uploader("📂 Upload a CSV file", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.success("✅ File uploaded successfully!")
    st.dataframe(df.head())

    insights = generate_ai_insights(df, department)
    st.markdown(insights)

    charts = show_charts(df)

    # Export options
    st.subheader("📤 Export Options")
    insights_text = insights.replace("#", "").replace("*", "")
    pdf_data = generate_pdf_report(insights_text, charts or [], department)
    st.download_button(
        label="📄 Download PDF Report",
        data=pdf_data,
        file_name=f"{department}_AI_Report.pdf",
        mime="application/pdf"
    )

    # Excel Export
    excel_data = BytesIO()
    with pd.ExcelWriter(excel_data, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Data')
    excel_data.seek(0)
    st.download_button(
        label="📊 Download Excel Summary",
        data=excel_data,
        file_name=f"{department}_Data_Summary.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

else:
    st.info("Upload a CSV file to begin AI analysis.")
