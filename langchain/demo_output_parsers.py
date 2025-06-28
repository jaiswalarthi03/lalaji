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
    print("\n=== Output Parsers Demo ===")
    print("This demo simulates parsing LLM output into structured data.")
    text = input_with_timeout("Enter a sentence to extract entities from: ", default="this is car")
    try:
        llm = TogetherLLM()
        prompt = f"Extract all named entities from this sentence as a Python list: {text}"
        print("Parsing with LLM...")
        result = llm.chat("meta-llama/Llama-3.3-70B-Instruct-Turbo-Free", prompt)
        print(f"\nParsed Output: {result}")
    except Exception as e:
        print(f"LLM unavailable: {e}")

if __name__ == "__main__":
    main() 