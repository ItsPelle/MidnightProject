import streamlit as st
import pandas as pd

st.set_page_config(page_title="AI Business Analytics", layout="wide")

st.title("📊 AI Analytics MVP")
st.write("Welcome to the prototype AI system that simplifies complex business reports into easy insights.")

uploaded_file = st.file_uploader("Upload your data file (CSV format)", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.subheader("Preview of your data:")
    st.dataframe(df.head())

    st.subheader("Quick Summary:")
    st.write(df.describe())

    st.success("✅ Analysis complete. Future updates will include automated insights and recommendations.")
