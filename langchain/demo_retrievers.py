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
    print("\n=== Retrievers Demo ===")
    print("This demo simulates a retriever that fetches information using an LLM.")
    query = input_with_timeout("Enter your retrieval query: ", default="hi")
    try:
        llm = TogetherLLM()
        print("Retrieving with LLM...")
        answer = llm.chat("meta-llama/Llama-3.3-70B-Instruct-Turbo-Free", f"Retrieve information about: {query}")
        print(f"\nRetriever Output: {answer}")
    except Exception as e:
        print(f"LLM unavailable: {e}")

if __name__ == "__main__":
    main() 