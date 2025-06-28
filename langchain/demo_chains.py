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
    print("\n=== Chains Demo ===")
    print("This demo simulates a simple chain of two steps.")
    name = input_with_timeout("Step 1: What's your name? ", default="Arvin")
    print(f"Step 2: Hello, {name.upper()}! (Name in uppercase)")

if __name__ == "__main__":
    main() 