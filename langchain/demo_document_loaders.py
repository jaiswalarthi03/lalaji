import sys
import threading
from LLM import TogetherLLM

def input_with_timeout(prompt, timeout=1, default=None):
    result = [default]
    def inner():
        try:
            result[0] = input(prompt)
        except Exception:
            pass
    t = threading.Thread(target=inner)
    t.daemon = True
    t.start()
    t.join(timeout)
    return result[0]

def main():
    print("\n=== Document Loaders Demo ===")
    print("This demo simulates loading a document and summarizing it with an LLM.")
    content = input_with_timeout("Paste your document text here: ", default="This is a sample document about a rich boy.")
    try:
        llm = TogetherLLM()
        prompt = f"Summarize this document: {content}"
        print("Summarizing with LLM...")
        summary = llm.chat("meta-llama/Llama-3.3-70B-Instruct-Turbo-Free", prompt)
        print(f"\nDocument Summary: {summary}")
    except Exception as e:
        print(f"LLM unavailable: {e}")

if __name__ == "__main__":
    main() 