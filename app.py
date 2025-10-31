import streamlit as st
import pandas as pd

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="AI Organizational Insights System",
    page_icon="🧠",
    layout="wide"
)

# --- SIDEBAR ---
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/a/a7/Artificial_Intelligence_Logo.svg/1024px-Artificial_Intelligence_Logo.svg.png", width=100)
st.sidebar.title("AI Organizational Insights System")
st.sidebar.markdown("---")
selected_section = st.sidebar.radio(
    "Choose section:",
    ["Overview", "Finance Department", "Marketing Department", "Membership Department", "HR Department", "Upload & Analyze Data"]
)
st.sidebar.markdown("---")
st.sidebar.info("Developed by Apelles Kamau 🇰🇪")

# --- TITLE ---
st.title("🤖 AI Organizational Insights System")
st.write("An intelligent data analysis dashboard that helps organizations summarize and interpret key performance data from different departments.")

# --- FILE UPLOAD ---
uploaded_file = st.file_uploader("Upload a CSV file for analysis", type=["csv"])

# --- FUNCTION TO GENERATE AI-STYLE INSIGHTS ---
def generate_ai_insights(df):
    insights = []

    # Basic summaries
    insights.append(f"The dataset has **{df.shape[0]} rows** and **{df.shape[1]} columns**.")
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    if numeric_cols:
        insights.append("### 📊 Key Numerical Insights:")
        for col in numeric_cols:
            insights.append(f"- The **average of {col}** is {df[col].mean():,.2f}.")
            insights.append(f"- The **highest value in {col}** is {df[col].max():,.2f}, and the lowest is {df[col].min():,.2f}.")
    else:
        insights.append("No numeric data found for statistical summary.")

    # Text-based columns
    text_cols = df.select_dtypes(include=['object']).columns.tolist()
    if text_cols:
        insights.append("### 🧾 Text Data Overview:")
        for col in text_cols:
            top_values = df[col].value_counts().head(3)
            insights.append(f"- **{col}** most common values: {', '.join(top_values.index.astype(str))}")
    
    insights.append("---")
    insights.append("✅ *AI Summary Complete — this system can be expanded to automatically detect anomalies, trends, and department-specific recommendations.*")
    return "\n".join(insights)

# --- SECTION LOGIC ---
if selected_section == "Overview":
    st.subheader("System Overview")
    st.write("""
    This AI-powered system helps your organization interpret complex data from multiple departments —
    such as **Finance**, **Marketing**, **Membership**, and **Human Resources (HR)** — by generating
    easy-to-understand summaries and actionable insights.
    """)

elif selected_section == "Finance Department":
    st.subheader("💰 Finance Department Insights")
    st.write("This section will analyze financial reports, revenue trends, and expenditure breakdowns.")
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.dataframe(df.head())
        st.markdown(generate_ai_insights(df))

elif selected_section == "Marketing Department":
    st.subheader("📢 Marketing Department Insights")
    st.write("This section focuses on campaign performance, engagement data, and lead conversions.")
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.dataframe(df.head())
        st.markdown(generate_ai_insights(df))

elif selected_section == "Membership Department":
    st.subheader("👥 Membership Department Insights")
    st.write("This section provides data summaries for member growth, activity, and retention analysis.")
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.dataframe(df.head())
        st.markdown(generate_ai_insights(df))

elif selected_section == "HR Department":
    st.subheader("👔 Human Resource (HR) Department Insights")
    st.write("This area analyzes employee records, attendance, and performance data.")
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.dataframe(df.head())
        st.markdown(generate_ai_insights(df))

elif selected_section == "Upload & Analyze Data":
    st.subheader("📤 Upload Any Department CSV")
    st.write("Upload your file below and get instant summaries and AI insights:")
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.success("✅ File uploaded successfully!")
        st.dataframe(df.head())
        st.markdown(generate_ai_insights(df))
    else:
        st.warning("Please upload a CSV file to begin analysis.")
