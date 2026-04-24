
import requests
import os

from dotenv import load_dotenv
load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "openai/gpt-3.5-turbo"   

def generate(prompt):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost",  
        "X-Title": "CodeClash AI"
    }

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "You are a senior software engineer."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 600
    }

    response = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=30)

    if response.status_code != 200:
        raise Exception(f"OpenRouter API error: {response.text}")

    return response.json()["choices"][0]["message"]["content"]
