def main():
    print("\n=== Graph Structures Demo ===")
    print("Creating a simple in-memory graph...")
    graph = {"A": ["B"], "B": ["C"], "C": []}
    print(f"Nodes: {list(graph.keys())}")
    print(f"Edges: {[(src, dst) for src in graph for dst in graph[src]]}")
    print("Adjacency List:")
    for n in graph:
        print(f"  {n}: {graph[n]}")
    print("Neighbors of B:", graph["B"])

if __name__ == "__main__":
    main() 