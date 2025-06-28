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
    print("\n=== Storage Demo ===")
    print("This demo simulates storing and retrieving a value.")
    value = input_with_timeout("Enter a value to store: ", default="autotest-value")
    storage = value
    print(f"Stored value: {storage}")
    print(f"Retrieved value: {storage}")

if __name__ == "__main__":
    main() 