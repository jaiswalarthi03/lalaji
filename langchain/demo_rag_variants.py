from LLM import GeminiLLM
import numpy as np
import re

def get_embedding(llm, text):
    result = llm.embed(text)
    # Gemini returns a dict with 'values' key
    arr = result.get('values') if isinstance(result, dict) else None
    if arr and isinstance(arr, list) and len(arr) > 0:
        arr = arr[:10] if len(arr) > 10 else arr
        arr = np.array(arr)
        if arr.shape[0] == 10:
            return arr
        # pad if needed
        arr = np.pad(arr, (0, 10-len(arr)), 'constant')
        return arr
    # fallback: random
    return np.random.rand(10)

def cosine_sim(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def real_rag(query, docs):
    llm = GeminiLLM()
    doc_embeddings = [get_embedding(llm, doc) for doc in docs]
    query_emb = get_embedding(llm, query)
    sims = [cosine_sim(query_emb, emb) for emb in doc_embeddings]
    best_idx = int(np.argmax(sims))
    retrieved = docs[best_idx]
    prompt = f"Given the document: {retrieved}\nAnswer the question: {query}"
    answer = llm.chat(prompt)
    return answer, retrieved, sims

def main():
    print("\n=== Advanced RAG Variants Demo (Gemini) ===")
    docs = ["Alice is a friend of Bob.", "Bob works at Acme Corp."]
    query = "Where does Alice's friend work?"
    print(f"Docs: {docs}")
    print(f"Query: {query}")
    try:
        answer, retrieved, sims = real_rag(query, docs)
        print(f"Most relevant doc: {retrieved}")
        print(f"Cosine similarities: {sims}")
        print(f"RAG answer: {answer}")
    except Exception as e:
        print(f"RAG failed: {e}")

if __name__ == "__main__":
    main() 