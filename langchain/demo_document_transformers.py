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
    print("\n=== Document Transformers Demo ===")
    print("This demo simulates transforming a document (e.g., summarization, cleaning) with an LLM.")
    text = input_with_timeout("Paste your document text here: ", default="This is a demo document for testing.")
    try:
        llm = TogetherLLM()
        prompt = f"Clean and summarize this document: {text}"
        print("Transforming with LLM...")
        result = llm.chat("meta-llama/Llama-3.3-70B-Instruct-Turbo-Free", prompt)
        print(f"\nTransformed Document: {result}")
    except Exception as e:
        print(f"LLM unavailable: {e}")

if __name__ == "__main__":
    main() 