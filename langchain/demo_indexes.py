from LLM import GeminiLLM
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
    print("\n=== Indexes Demo ===")
    print("This demo simulates creating an index from a list of sentences using Gemini.")
    print("Enter sentences (type 'END' to finish):")
    sentences = []
    for default in ["this is a car", "this is a bus", "END"]:
        s = input_with_timeout("", default=default)
        if s.strip().upper() == 'END':
            break
        sentences.append(s)
    try:
        llm = GeminiLLM()
        prompt = f"Given these sentences, list the main topics as an index: {sentences}"
        print("Indexing with Gemini...")
        result = llm.chat(prompt)
        print(f"\nIndex: {result}")
    except Exception as e:
        print(f"Gemini unavailable: {e}")

if __name__ == "__main__":
    main() 