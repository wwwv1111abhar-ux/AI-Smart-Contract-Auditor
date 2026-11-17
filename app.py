import streamlit as st
import os
import requests
from dotenv import load_dotenv

# تنظیمات صفحه
st.set_page_config(page_title="AI Smart Contract Auditor", page_icon="🛡️", layout="wide")

# خواندن کلید از فایل .env
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

st.title("🛡️ AI Smart Contract Auditor")
st.markdown("Analyze your Solidity smart contracts for security vulnerabilities using AI.")

# دو ستون برای ورودی
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📝 Paste your Solidity code here:")
    solidity_code = st.text_area("", height=300, label_visibility="collapsed")

with col2:
    st.subheader("📂 Or upload a .sol file:")
    uploaded_file = st.file_uploader("Choose a file", type=["sol"])
    if uploaded_file is not None:
        solidity_code = uploaded_file.getvalue().decode("utf-8")
        st.success("File loaded successfully!")

st.divider()

if st.button("🔍 Run Security Audit", use_container_width=True):
    if not solidity_code.strip():
        st.warning("Please provide some Solidity code first.")
    elif not GROQ_API_KEY:
        st.error("API Key not found. Please check your .env file.")
    else:
        with st.spinner("AI is analyzing the contract..."):
            url = "https://api.groq.com/openai/v1/chat/completions"
            
            prompt = f"""
            You are an expert smart contract security auditor.
            Please analyze the following Solidity code.
            1. Identify any security vulnerabilities (e.g., Reentrancy, Access Control).
            2. Explain the impact of each vulnerability.
            3. Provide a secure version of the code.
            
            Here is the code:
            {solidity_code}
            """
            
            headers = {
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "openai/gpt-oss-120b",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1
            }
            
            try:
                response = requests.post(url, headers=headers, json=data)
                if response.status_code == 200:
                    result = response.json()
                    st.success("✅ Analysis Complete!")
                    st.markdown("### 📋 Security Report:")
                    st.markdown(result['choices'][0]['message']['content'])
                else:
                    st.error(f"API Error: {response.status_code}")
            except Exception as e:
                st.error(f"Network Error: {e}")
