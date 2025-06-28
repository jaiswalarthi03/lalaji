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
    print("\n=== Vectorstores Demo ===")
    print("This demo simulates storing and searching vectors using Gemini embeddings.")
    s1 = input_with_timeout("Enter first sentence: ", default="this is a car")
    s2 = input_with_timeout("Enter second sentence: ", default="this is a bus")
    try:
        llm = GeminiLLM()
        print("Generating embeddings with Gemini...")
        emb1 = llm.embed(s1)
        emb2 = llm.embed(s2)
        print(f"\nEmbedding 1: {emb1}\nEmbedding 2: {emb2}")
        print("Compare the embeddings for similarity (manual step in this demo).")
    except Exception as e:
        print(f"Gemini unavailable: {e}")

if __name__ == "__main__":
    main() 