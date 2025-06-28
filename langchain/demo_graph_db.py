import sys

def main():
    print("\n=== Graph DB Demo ===")
    print("Using in-memory graph (dict)...")
    graph = {}
    # Add nodes
    for node in ["Alice", "Bob"]:
        graph[node] = []
    # Add edge
    graph["Alice"].append(("Bob", "FRIEND"))
    # Query
    print("Nodes:", list(graph.keys()))
    print("Edges:", [(src, dst, rel) for src in graph for dst, rel in graph[src]])
    print("Query: Who are Alice's friends?")
    friends = [dst for dst, rel in graph["Alice"] if rel == "FRIEND"]
    print("Result:", ", ".join(friends) if friends else "None")

if __name__ == "__main__":
    main() 