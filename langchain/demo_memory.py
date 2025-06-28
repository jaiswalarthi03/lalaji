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
    print("\n=== Memory Demo ===")
    print("This demo simulates memory by recalling previous answers and summarizing them with an LLM.")
    answers = []
    answers.append(input_with_timeout("Q1: What's your favorite color? ", default="red"))
    answers.append(input_with_timeout("Q2: What's your favorite animal? ", default="tiger"))
    try:
        llm = TogetherLLM()
        prompt = f"Summarize this conversation: Q1: {answers[0]} Q2: {answers[1]}"
        print("Summarizing with LLM...")
        summary = llm.chat("meta-llama/Llama-3.3-70B-Instruct-Turbo-Free", prompt)
        print(f"\nLLM Summary: {summary}")
    except Exception as e:
        print(f"LLM unavailable: {e}")
    print(f"Memory: {answers}")

if __name__ == "__main__":
    main() 