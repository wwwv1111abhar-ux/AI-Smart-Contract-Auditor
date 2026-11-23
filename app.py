import streamlit as st
import os
import requests
import time
from web3 import Web3
from dotenv import load_dotenv

# تنظیمات صفحه
st.set_page_config(page_title="AI Smart Contract Auditor & Guardian", page_icon="🛡️", layout="wide")

# خواندن کلید از فایل .env
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
RPC_URL = "https://ethereum-sepolia-rpc.publicnode.com"

# کد نمونه برای دکمه تست
sample_code = """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract VulnerableFund {
    mapping(address => uint256) public balances;
    address public owner;

    constructor() { owner = msg.sender; }

    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }

    function withdrawAll() public {
        uint256 balance = balances[msg.sender];
        require(balance > 0, "No balance");
        (bool success, ) = msg.sender.call{value: balance}("");
        require(success, "Transfer failed");
        balances[msg.sender] = 0;
    }

    function emergencyWithdraw() public {
        (bool success, ) = msg.sender.call{value: address(this).balance}("");
        require(success, "Emergency withdraw failed");
    }
}"""

st.title("🛡️ AI Smart Contract Auditor & Guardian Agent")
st.markdown("Analyze your Solidity smart contracts or let the autonomous agent monitor the blockchain for new threats.")

# ساخت دو تب
tab1, tab2 = st.tabs(["🔍 Manual Code Audit", "🤖 Live Guardian Agent"])

# ----------------- تب اول: تحلیل دستی کد -----------------
with tab1:
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("📝 Paste your Solidity code here:")
        
        if st.button("✨ Load Sample Code"):
            st.session_state['code_input'] = sample_code
            
        solidity_code = st.text_area("Solidity Code", value=st.session_state.get('code_input', ''), height=300, key="code_area")

    with col2:
        st.subheader("📂 Or upload a .sol file:")
        uploaded_file = st.file_uploader("Choose a file", type=["sol"])
        if uploaded_file is not None:
            solidity_code = uploaded_file.getvalue().decode("utf-8")
            st.success("File loaded successfully!")

    if st.button("🔍 Run Security Audit", use_container_width=True):
        if not solidity_code.strip():
            st.warning("Please provide some Solidity code first.")
        elif not GROQ_API_KEY:
            st.error("API Key not found. Please check your .env file.")
        else:
            with st.spinner("AI is analyzing the contract..."):
                url = "https://api.groq.com/openai/v1/chat/completions"
                prompt = f"You are an expert smart contract security auditor. Analyze this Solidity code for vulnerabilities:\n{solidity_code}"
                headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
                data = {"model": "openai/gpt-oss-120b", "messages": [{"role": "user", "content": prompt}], "temperature": 0.1}
                
                try:
                    response = requests.post(url, headers=headers, json=data)
                    if response.status_code == 200:
                        st.success("✅ Analysis Complete!")
                        st.markdown("### 📋 Security Report:")
                        st.markdown(response.json()['choices'][0]['message']['content'])
                    else:
                        st.error(f"API Error: {response.status_code}")
                except Exception as e:
                    st.error(f"Network Error: {e}")

# ----------------- تب دوم: ایجنت خودمختار -----------------
with tab2:
    st.subheader("🤖 Autonomous Agent")
    st.write("This agent connects to the Ethereum Sepolia testnet and monitors for newly deployed smart contracts, automatically analyzing them with AI.")
    
    if st.button("▶️ Start Monitoring", use_container_width=True):
        w3 = Web3(Web3.HTTPProvider(RPC_URL))
        
        if not w3.is_connected():
            st.error("❌ Failed to connect to blockchain.")
        else:
            st.info(f"✅ Connected to Sepolia. Latest block: {w3.eth.block_number}")
            status_text = st.empty()
            report_container = st.container()
            
            last_block = w3.eth.block_number
            # برای جلوگیری از بلاک شدن کل برنامه، ۵ بلاک رو چک می‌کنیم
            for i in range(5): 
                current_block = w3.eth.block_number
                if current_block > last_block:
                    status_text.info(f"🔍 Scanning block: {current_block}...")
                    block = w3.eth.get_block(current_block, full_transactions=True)
                    
                    for tx in block.transactions:
                        if tx.to is None: # قرارداد جدید
                            receipt = w3.eth.get_transaction_receipt(tx.hash)
                            contract_address = receipt.contractAddress
                            with report_container:
                                st.warning(f"⚠️ New Contract Detected: {contract_address}")
                                with st.spinner("Analyzing with AI..."):
                                    url = "https://api.groq.com/openai/v1/chat/completions"
                                    prompt = f"Analyze this contract for security. Address: {contract_address}"
                                    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
                                    data = {"model": "openai/gpt-oss-120b", "messages": [{"role": "user", "content": prompt}], "temperature": 0.1}
                                    resp = requests.post(url, headers=headers, json=data)
                                    if resp.status_code == 200:
                                        st.success("Analysis Complete:")
                                        st.markdown(resp.json()['choices'][0]['message']['content'])
                    last_block = current_block
                time.sleep(2)
            status_text.success("✅ Scan complete.")
