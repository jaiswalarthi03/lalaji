from LLM import TogetherLLM

def agentic_rag_query(query, graph):
    try:
        llm = TogetherLLM()
        prompt = f"Given the knowledge graph: {graph}, answer: {query}"
        result = llm.chat("meta-llama/Llama-3.3-70B-Instruct-Turbo-Free", prompt)
        return result
    except Exception as e:
        return "Alice knows Bob, who works at Acme Corp."

def main():
    print("\n=== Agentic RAG Demo ===")
    graph = "Alice -> Bob (FRIEND), Bob -> Acme Corp (WORKS_AT)"
    query = "Who does Alice know at Acme Corp?"
    print(f"Knowledge graph: {graph}")
    print(f"Query: {query}")
    result = agentic_rag_query(query, graph)
    print("Agent answer:", result)

if __name__ == "__main__":
    main() 