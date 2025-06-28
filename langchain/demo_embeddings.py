from LLM import GeminiLLM

def main():
    print("\n=== Embeddings Demo ===")
    print("This demo generates a real embedding using Google Gemini.")
    text = input("Enter a sentence to embed: ")
    try:
        llm = GeminiLLM()
        print("Generating embedding with Gemini...")
        embedding = llm.embed(text)
        print(f"\nGemini Embedding: {embedding}")
    except Exception as e:
        print(f"Gemini LLM unavailable: {e}")

if __name__ == "__main__":
    main() 