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
    print("\n=== Runnables Demo ===")
    print("This demo simulates a runnable that transforms input using an LLM.")
    text = input_with_timeout("Enter a sentence to turn into a poem: ", default="i am a rich boy")
    try:
        llm = TogetherLLM()
        prompt = f"Rewrite this as a short poem: {text}"
        print("Running LLM runnable...")
        poem = llm.chat("meta-llama/Llama-3.3-70B-Instruct-Turbo-Free", prompt)
        print(f"\nRunnable Output (Poem):\n{poem}")
    except Exception as e:
        print(f"LLM unavailable: {e}")

if __name__ == "__main__":
    main() 