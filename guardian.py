import os
import time
import requests
from web3 import Web3
from dotenv import load_dotenv

# خواندن کلیدها از فایل .env
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
# یک RPC رایگان برای شبکه تستی Sepolia
RPC_URL = "https://ethereum-sepolia-rpc.publicnode.com" 

# اتصال به شبکه
w3 = Web3(Web3.HTTPProvider(RPC_URL))

if not w3.is_connected():
    print("❌ خطا در اتصال به شبکه.")
    exit()

print(f"✅ ایجنت به شبکه متصل شد. آخرین بلاک: {w3.eth.block_number}")

def analyze_contract_with_ai(contract_address, bytecode):
    """ارسال بایت‌کد قرارداد به هوش مصنوعی"""
    url = "https://api.groq.com/openai/v1/chat/completions"
    
    prompt = f"""
    You are an autonomous security agent. Analyze the following smart contract bytecode for critical vulnerabilities.
    Contract Address: {contract_address}
    Bytecode snippet: {bytecode[:400]}... (truncated)
    
    Is this contract safe? Answer in a brief, actionable way.
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
            return response.json()['choices'][0]['message']['content']
        else:
            return f"API Error: {response.status_code}"
    except Exception as e:
        return f"Network Error: {e}"

def monitor_agent():
    """رصد بلاک‌های جدید و قراردادهای دیپلوی شده"""
    print("🤖 ایجنت شروع به کار کرد... در حال رصد قراردادهای جدید...")
    last_block = w3.eth.block_number
    
    while True:
        try:
            current_block = w3.eth.block_number
            if current_block > last_block:
                print(f"\n🔍 بلاک جدید: {current_block}")
                block = w3.eth.get_block(current_block, full_transactions=True)
                
                for tx in block.transactions:
                    # اگر تراکنش ایجاد قرارداد جدید باشد (to خالی است)
                    if tx.to is None:
                        receipt = w3.eth.get_transaction_receipt(tx.hash)
                        contract_address = receipt.contractAddress
                        print(f"⚠️ قرارداد جدید پیدا شد: {contract_address}")
                        
                        code = w3.eth.get_code(contract_address).hex()
                        if code != "0x":
                            print("🧠 در حال تحلیل با هوش مصنوعی...")
                            analysis = analyze_contract_with_ai(contract_address, code)
                            print(f"📋 گزارش امنیتی:\n{analysis}")
                            
                last_block = current_block
            time.sleep(5) # هر ۵ ثانیه چک می‌کند
        except Exception as e:
            print(f"خطا: {e}")
            time.sleep(10)

if __name__ == "__main__":
    monitor_agent()
