from LLM import TogetherLLM, GeminiLLM

def main():
    print("\n=== LLM Abstraction Demo ===")
    print("Simulating LLM selection based on context length...")
    context_length = 2048
    print(f"Context length: {context_length}")
    prompt = "Hello! You are a helpful assistant."
    if context_length < 4096:
        print("Selected model: Together Llama-3.3-70B-Instruct-Turbo-Free")
        try:
            llm = TogetherLLM()
            response = llm.chat("meta-llama/Llama-3.3-70B-Instruct-Turbo-Free", prompt)
            print(f"LLM response: {response}")
        except Exception as e:
            print(f"Together LLM unavailable: {e}")
    else:
        print("Selected model: Google Gemini 2.0 Flash")
        try:
            llm = GeminiLLM()
            response = llm.chat(prompt)
            print(f"Gemini response: {response}")
        except Exception as e:
            print(f"Gemini unavailable: {e}")
    print("Meta-prompting: [SYSTEM] You are a helpful assistant. [USER] Hello!")

if __name__ == "__main__":
    main() 