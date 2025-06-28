import time
import requests
from config import TOGETHER_API_KEY, GEMINI_API_KEY

API_URL = "https://api.together.xyz/v1/chat/completions"
IMG_URL = "https://api.together.xyz/v1/images/generations"
GEMINI_CHAT_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}" if GEMINI_API_KEY else None
GEMINI_EMBED_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-exp-03-07:embedContent?key={GEMINI_API_KEY}" if GEMINI_API_KEY else None

CHAT_MODELS = [
    ("meta-llama/Llama-3.3-70B-Instruct-Turbo-Free", "Llama 3.3 70B Turbo Free (Together)"),
    ("lgai/exaone-3-5-32b-instruct", "Exaone 3.5 32B Instruct (Together)"),
    ("lgai/exaone-deep-32b", "Exaone Deep 32B (Together)"),
    ("deepseek-ai/DeepSeek-R1-Distill-Llama-70B-free", "DeepSeek R1 Distill Llama 70B Free (Together)"),
    ("meta-llama/Llama-Vision-Free", "Llama Vision Free (Together)"),
    ("arcee-ai/AFM-4.5B-Preview", "AFM 4.5B Preview (Together)"),
    ("gemini", "Google Gemini 2.0 Flash (Gemini)")
]
IMG_MODELS = [
    ("black-forest-labs/FLUX.1-schnell-Free", "FLUX.1 Schnell Free (Together)"),
]

class TogetherLLM:
    def __init__(self, api_key=None):
        self.api_key = api_key or TOGETHER_API_KEY
        if not self.api_key or self.api_key.startswith("your-"):
            raise ValueError("TOGETHER_API_KEY not set in config.py.")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def chat(self, model, prompt):
        data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False
        }
        try:
            resp = requests.post(API_URL, headers=self.headers, json=data)
            if resp.status_code == 429:
                print("Rate limit hit. Waiting 10 seconds...")
                time.sleep(10)
                return self.chat(model, prompt)
            resp.raise_for_status()
            result = resp.json()
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            return f"Error: {e}"

    def generate_image(self, model, prompt):
        data = {
            "model": model,
            "prompt": prompt
        }
        try:
            resp = requests.post(IMG_URL, headers=self.headers, json=data)
            if resp.status_code == 429:
                print("Rate limit hit. Waiting 10 seconds...")
                time.sleep(10)
                return self.generate_image(model, prompt)
            resp.raise_for_status()
            result = resp.json()
            return result.get("data", [{}])[0].get("url", "No image URL returned.")
        except Exception as e:
            return f"Error: {e}"

class GeminiLLM:
    def __init__(self, api_key=None):
        self.api_key = api_key or GEMINI_API_KEY
        if not self.api_key or self.api_key.startswith("your-"):
            raise ValueError("GEMINI_API_KEY not set in config.py.")
        self.chat_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={self.api_key}"
        self.embed_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-exp-03-07:embedContent?key={self.api_key}"
        self.headers = {"Content-Type": "application/json"}

    def chat(self, prompt):
        data = {
            "contents": [
                {"parts": [{"text": prompt}]}
            ]
        }
        try:
            resp = requests.post(self.chat_url, headers=self.headers, json=data)
            if resp.status_code == 429:
                print("Gemini rate limit hit. Waiting 10 seconds...")
                time.sleep(10)
                return self.chat(prompt)
            resp.raise_for_status()
            result = resp.json()
            return result["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            return f"Error: {e}"

    def embed(self, text, task_type=None):
        data = {
            "model": "models/gemini-embedding-exp-03-07",
            "content": {"parts": [{"text": text}]}
        }
        if task_type:
            data["taskType"] = task_type
        try:
            resp = requests.post(self.embed_url, headers=self.headers, json=data)
            if resp.status_code == 429:
                print("Gemini embedding rate limit hit. Waiting 10 seconds...")
                time.sleep(10)
                return self.embed(text, task_type)
            resp.raise_for_status()
            result = resp.json()
            return result.get("embedding", result)
        except Exception as e:
            return f"Error: {e}"

def main():
    print("\n=== LLM & Image Demo (Together.xyz & Google Gemini) ===")
    print("Select a model:")
    for i, (_, name) in enumerate(CHAT_MODELS, 1):
        print(f"{i}. {name}")
    print(f"{len(CHAT_MODELS)+1}. Image Generation (Together)")
    print(f"{len(CHAT_MODELS)+2}. Gemini Embedding")
    try:
        choice = int(input("Enter your choice: "))
    except ValueError:
        print("Invalid input.")
        return
    if 1 <= choice <= len(CHAT_MODELS):
        model, name = CHAT_MODELS[choice-1]
        prompt = input(f"Enter your prompt for {name}: ")
        if model == "gemini":
            try:
                llm = GeminiLLM()
                print("Waiting for Gemini response...")
                response = llm.chat(prompt)
                print(f"\nGemini Response:\n{response}")
            except Exception as e:
                print(e)
        else:
            try:
                llm = TogetherLLM()
                print("Waiting for Together response...")
                response = llm.chat(model, prompt)
                print(f"\nResponse:\n{response}")
            except Exception as e:
                print(e)
    elif choice == len(CHAT_MODELS)+1:
        model, name = IMG_MODELS[0]
        prompt = input(f"Enter your image prompt for {name}: ")
        try:
            llm = TogetherLLM()
            print("Waiting for image URL...")
            url = llm.generate_image(model, prompt)
            print(f"\nImage URL: {url}")
        except Exception as e:
            print(e)
    elif choice == len(CHAT_MODELS)+2:
        prompt = input("Enter text to embed with Gemini: ")
        task_type = input("Optional: Enter Gemini embedding task type (or leave blank): ") or None
        try:
            llm = GeminiLLM()
            print("Waiting for Gemini embedding...")
            embedding = llm.embed(prompt, task_type)
            print(f"\nGemini Embedding: {embedding}")
        except Exception as e:
            print(e)
    else:
        print("Invalid choice.")

if __name__ == "__main__":
    main() 