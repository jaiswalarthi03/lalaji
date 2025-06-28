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
    print("\n=== Tools Demo ===")
    print("This demo simulates a tool that uses an LLM to answer a question.")
    question = input_with_timeout("Ask any question: ", default="this is a das")
    try:
        llm = TogetherLLM()
        print("Calling LLM tool...")
        answer = llm.chat("meta-llama/Llama-3.3-70B-Instruct-Turbo-Free", question)
        print(f"\nTool (LLM) Answer: {answer}")
    except Exception as e:
        print(f"LLM unavailable: {e}")

if __name__ == "__main__":
    main() 