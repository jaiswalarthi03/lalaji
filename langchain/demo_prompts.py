import sys
import threading

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
    print("\n=== Prompts Demo ===")
    print("This demo simulates a prompt template.")
    topic = input_with_timeout("Enter a topic: ", default="hi this is a demo")
    prompt = f"Write a short story about {topic}."
    print(f"Prompt: {prompt}")

if __name__ == "__main__":
    main() 