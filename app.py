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

# کد نمونه برای دکمه تست
sample_code = """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract VulnerableFund {
    mapping(address => uint256) public balances;
    address public owner;
    uint256 public totalFunds;

    constructor() { owner = msg.sender; }

    function deposit() public payable {
        balances[msg.sender] += msg.value;
        totalFunds += msg.value;
    }

    function withdrawAll() public {
        uint256 balance = balances[msg.sender];
        require(balance > 0, "No balance");
        (bool success, ) = msg.sender.call{value: balance}("");
        require(success, "Transfer failed");
        balances[msg.sender] = 0;
        totalFunds -= balance;
    }

    function playLottery() public payable {
        require(msg.value == 1 ether, "Must send 1 ETH");
        if (block.timestamp % 2 == 0) {
            payable(msg.sender).transfer(2 ether);
        }
    }

    function emergencyWithdraw() public {
        (bool success, ) = msg.sender.call{value: address(this).balance}("");
        require(success, "Emergency withdraw failed");
    }
}"""

# دو ستون برای ورودی
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📝 Paste your Solidity code here:")
    
    # دکمه برای قرار دادن کد نمونه
    if st.button("✨ Load Sample Code"):
        st.session_state['code_input'] = sample_code
        
    # کادر متن که مقدارش از session_state خونده میشه
    solidity_code = st.text_area("Solidity Code", value=st.session_state.get('code_input', ''), height=300)

with col2:
    st.subheader("📂 Or upload a .sol file:")
    uploaded_file = st.file_uploader("Choose a file", type=["sol"])
    if uploaded_file is not None:
        solidity_code = uploaded_file.getvalue().decode("utf-8")
        st.success("File loaded successfully!")

st.divider()

# دکمه اصلی برای تحلیل
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
