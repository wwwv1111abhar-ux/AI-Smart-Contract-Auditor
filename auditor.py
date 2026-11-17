import os
import requests
from dotenv import load_dotenv

# خواندن کلید از فایل .env
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

url = "https://api.groq.com/openai/v1/chat/completions"

solidity_code = """
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract VulnerableBank {
    mapping(address => uint256) public balances;

    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }

    function withdraw() public {
        uint256 balance = balances[msg.sender];
        require(balance > 0, "Insufficient balance");
        (bool success, ) = msg.sender.call{value: balance}("");
        require(success, "Transfer failed");
        balances[msg.sender] = 0;
    }
}
"""

prompt = f"""
You are an expert smart contract security auditor.
Please analyze the following Solidity code.
1. Identify any security vulnerabilities (like reentrancy, access control, etc.).
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

print("⏳ در حال ارسال کد به هوش مصنوعی برای تحلیل امنیتی...")

try:
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        result = response.json()
        print("\n✅ تحلیل هوش مصنوعی:")
        print("--------------------------------------------------")
        print(result['choices'][0]['message']['content'])
        print("--------------------------------------------------")
    else:
        print(f"❌ خطا در ارتباط با API: {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"خطای شبکه: {e}"))
