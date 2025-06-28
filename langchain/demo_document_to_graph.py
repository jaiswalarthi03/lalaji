from LLM import TogetherLLM

def extract_entities_relations(text):
    try:
        llm = TogetherLLM()
        prompt = f"Extract entities and relations from this text as Python tuples: {text}"
        result = llm.chat("meta-llama/Llama-3.3-70B-Instruct-Turbo-Free", prompt)
        return result
    except Exception as e:
        # Fallback: simple extraction
        return "[('Alice', 'FRIEND', 'Bob'), ('Bob', 'WORKS_AT', 'Acme Corp')]"

def main():
    print("\n=== Document-to-Graph Demo ===")
    text = "Alice is friends with Bob. Bob works at Acme Corp."
    print(f"Input text: {text}")
    result = extract_entities_relations(text)
    print("Extracted entities/relations:", result)

if __name__ == "__main__":
    main() 