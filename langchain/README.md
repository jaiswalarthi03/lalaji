# LangChain & LangGraph Standalone Demos

This folder contains standalone Python command-line demos for each major feature of LangChain and LangGraph, as summarized in `../features.md`.

Each demo is minimal, self-contained, and runnable independently. The main entry point is `app.py`, which provides a menu to run each demo.

## How to Use

- Run `python app.py` to see a menu of all available feature demos.
- Each demo can also be run directly as a script (e.g., `python demo_agents.py`).

## Planned Demo Files

- `app.py` — Main CLI menu to run all demos
- `demo_agents.py` — Agents (multi-step, tool-using, etc.)
- `demo_chains.py` — Chains (composable workflows)
- `demo_callbacks.py` — Callbacks and event hooks
- `demo_prompts.py` — Prompt templates and management
- `demo_memory.py` — Memory (short/long-term)
- `demo_tools.py` — Tool integrations (API, search, code exec)
- `demo_runnables.py` — Runnables (functions, chains, etc.)
- `demo_retrievers.py` — Retrieval from various backends
- `demo_embeddings.py` — Embeddings and similarity search
- `demo_document_loaders.py` — Document ingestion
- `demo_document_transformers.py` — Document preprocessing
- `demo_output_parsers.py` — Output parsing from LLMs
- `demo_indexes.py` — Indexing for fast retrieval
- `demo_vectorstores.py` — Vector DB integrations
- `demo_storage.py` — Pluggable storage backends
- `demo_graph_db.py` — Graph database integrations
- `demo_graph_structures.py` — Graph data structures and manipulation
- `demo_graph_indexing.py` — Graph indexing and search
- `demo_graph_visualization.py` — Graph visualization (ASCII, Mermaid, PNG)
- `demo_graph_workflows.py` — Graph workflows and branching
- `demo_document_to_graph.py` — Document-to-graph conversion
- `demo_agentic_rag.py` — Agentic RAG with graphs
- `demo_llms.py` — LLM provider abstraction
- `demo_chat_models.py` — Chat model abstraction
- `demo_evaluation.py` — LLM and chain evaluation
- `demo_sql.py` — SQL database QA and retrieval
- `demo_multimodal.py` — Multi-modal (image, video, text)
- `demo_custom_tools.py` — Custom tool integration
- `demo_external_systems.py` — External API/DB/service integration
- `demo_devops.py` — DevOps: pre-commit, Makefile, CI/CD, containers
- `demo_docs.py` — API reference, tutorials, guides, cookbook

---

Each file contains a minimal CLI demo for its feature. For details on each feature, see `../features.md`. 