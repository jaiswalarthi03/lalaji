from LLM import TogetherLLM, GeminiLLM

def main():
    print("\n=== Chat Model Abstraction Demo ===")
    print("Calling Together Llama-3.3-70B chat model...")
    try:
        llm = TogetherLLM()
        response = llm.chat("meta-llama/Llama-3.3-70B-Instruct-Turbo-Free", "Hello from Together!")
        print(f"Together response: {response}")
    except Exception as e:
        print(f"Together LLM unavailable: {e}")
    print("Calling Google Gemini chat model...")
    try:
        gemini = GeminiLLM()
        response = gemini.chat("Hello from Gemini!")
        print(f"Gemini response: {response}")
    except Exception as e:
        print(f"Gemini unavailable: {e}")

if __name__ == "__main__":
    main() 