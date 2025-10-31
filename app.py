import streamlit as st
import pandas as pd

st.set_page_config(page_title="AI Business Analytics", layout="wide")

st.title("📊 AI Business Analytics MVP")
st.write("This tool simplifies complex departmental reports into easy summaries and insights.")

uploaded_file = st.file_uploader("📤 Upload your data file (CSV format)", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.subheader("🧾 Preview of your Data:")
    st.dataframe(df.head())

    st.subheader("📈 Summary Statistics:")
    st.write(df.describe())

    # --- Simple insight generation ---
    st.subheader("💡 Automated Insights:")
    numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns

    if len(numeric_cols) > 0:
        for col in numeric_cols:
            mean_val = df[col].mean()
            max_val = df[col].max()
            min_val = df[col].min()

            st.markdown(f"**{col}** → Average: `{mean_val:.2f}`, Range: `{min_val:.2f} - {max_val:.2f}`")

        st.success("✅ Analysis complete. These summaries will later be enhanced with AI-driven recommendations.")
    else:
        st.warning("No numeric data found to analyze.")
else:
    st.info("Please upload a CSV report to start analysis.")
