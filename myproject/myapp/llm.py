import requests
import os

OLLAMA_URL = "http://localhost:11434/api/generate"
OPENAI_KEY = os.environ.get("OPENAI_API_KEY")

def generate_with_ollama(prompt):
    try:
        r = requests.post(OLLAMA_URL, json={"models": "llama3", "prompt": prompt})
        return r.json().get("response", "")
    except:
        return None

def generate_with_openai(prompt):
    if not OPENAI_KEY: return None
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {OPENAI_KEY}"}
    data = {
        "models": "gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}],
    }
    r = requests.post(url, headers=headers, json=data)
    return r.json()["choices"][0]["message"]["content"]

def generate_explanation(prompt):
    res = generate_with_ollama(prompt)
    if res: return res
    return generate_with_openai(prompt) or "No explanation available."
