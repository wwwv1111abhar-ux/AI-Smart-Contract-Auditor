import streamlit as st
import os
import requests
from dotenv import load_dotenv

# تنظیمات صفحه
st.set_page_config(page_title="AI Smart Contract Auditor", page_icon="🛡️")

# خواندن کلید از فایل .env
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

st.title("🛡️ AI Smart Contract Auditor")
st.write("قرارداد هوشمند خود را وارد کنید تا هوش مصنوعی آن را از نظر امنیتی بررسی کند.")

# کادر برای وارد کردن کد
solidity_code = st.text_area("کد Solidity خود را اینجا پیست کنید:", height=300)

if st.button("تحلیل امنیتی 🔍"):
    if not solidity_code.strip():
        st.warning("لطفاً ابتدا کد قرارداد را وارد کنید.")
    elif not GROQ_API_KEY:
        st.error("کلید API یافت نشد. لطفاً فایل .env را بررسی کنید.")
    else:
        with st.spinner("در حال تحلیل کد توسط هوش مصنوعی..."):
            url = "https://api.groq.com/openai/v1/chat/completions"
            
            prompt = f"""
            You are an expert smart contract security auditor.
            Please analyze the following Solidity code.
            1. Identify any security vulnerabilities.
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
                    st.success("تحلیل با موفقیت انجام شد!")
                    st.markdown("### 📝 گزارش امنیتی:")
                    st.markdown(result['choices'][0]['message']['content'])
                else:
                    st.error(f"خطا در ارتباط با API: {response.status_code}")
            except Exception as e:
                st.error(f"خطای شبکه: {e}")
