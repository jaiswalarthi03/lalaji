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
    print("\n=== Agents Demo ===")
    print("This demo simulates a simple agent that asks and answers a question.")
    user_input = input_with_timeout("Agent: What's your favorite programming language? ", default="Python")
    print(f"Agent: Oh, {user_input} is a great choice!")

if __name__ == "__main__":
    main() 