from LLM import TogetherLLM, GeminiLLM

def main():
    print("\n=== Multi-modal Demo ===")
    print("Generating an image with Together API...")
    try:
        llm = TogetherLLM()
        prompt = "A cat sitting on a sofa."
        url = llm.generate_image("black-forest-labs/FLUX.1-schnell-Free", prompt)
        print(f"Generated image URL: {url}")
    except Exception as e:
        print(f"Image generation unavailable: {e}")
    print("\nCaptioning the image with Gemini...")
    try:
        gemini = GeminiLLM()
        caption = gemini.chat("Describe an image of a cat sitting on a sofa.")
        print(f"Gemini caption: {caption}")
    except Exception as e:
        print(f"Gemini unavailable: {e}")

if __name__ == "__main__":
    main() 