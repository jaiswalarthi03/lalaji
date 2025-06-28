import os
import subprocess

DEMO_FILES = [
    ("Agents", "demo_agents.py"),
    ("Chains", "demo_chains.py"),
    ("Callbacks", "demo_callbacks.py"),
    ("Prompts", "demo_prompts.py"),
    ("Memory", "demo_memory.py"),
    ("Tools", "demo_tools.py"),
    ("Runnables", "demo_runnables.py"),
    ("Retrievers", "demo_retrievers.py"),
    ("Embeddings", "demo_embeddings.py"),
    ("Document Loaders", "demo_document_loaders.py"),
    ("Document Transformers", "demo_document_transformers.py"),
    ("Output Parsers", "demo_output_parsers.py"),
    ("Indexes", "demo_indexes.py"),
    ("Vectorstores", "demo_vectorstores.py"),
    ("Storage", "demo_storage.py"),
    ("Graph DB", "demo_graph_db.py"),
    ("Graph Structures", "demo_graph_structures.py"),
    ("Graph Indexing", "demo_graph_indexing.py"),
    ("Graph Visualization", "demo_graph_visualization.py"),
    ("Graph Workflows", "demo_graph_workflows.py"),
    ("Document-to-Graph", "demo_document_to_graph.py"),
    ("Agentic RAG", "demo_agentic_rag.py"),
    ("LLMs", "demo_llms.py"),
    ("Chat Models", "demo_chat_models.py"),
    ("Evaluation", "demo_evaluation.py"),
    ("SQL", "demo_sql.py"),
    ("Multi-modal", "demo_multimodal.py"),
    ("Custom Tools", "demo_custom_tools.py"),
    ("External Systems", "demo_external_systems.py"),
    ("DevOps", "demo_devops.py"),
    ("Docs & Demos", "demo_docs.py"),
]

def main():
    while True:
        print("\nLangChain & LangGraph Feature Demos:")
        for i, (name, _) in enumerate(DEMO_FILES, 1):
            print(f"{i}. {name}")
        print("0. Exit")
        try:
            choice = int(input("Select a demo to run: "))
        except ValueError:
            print("Invalid input. Please enter a number.")
            continue
        if choice == 0:
            break
        if 1 <= choice <= len(DEMO_FILES):
            _, filename = DEMO_FILES[choice - 1]
            if os.path.exists(filename):
                subprocess.run(["python", filename])
            else:
                print(f"Demo file '{filename}' not found.")
        else:
            print("Invalid choice. Try again.")

if __name__ == "__main__":
    main() 