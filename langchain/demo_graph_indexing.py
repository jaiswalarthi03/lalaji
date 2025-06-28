def main():
    print("\n=== Graph Indexing Demo ===")
    print("Building index for in-memory graph...")
    graph = {"A": ["B"], "B": ["C"], "C": []}
    index = {node: i for i, node in enumerate(graph.keys())}
    print(f"Index: {index}")
    node = "B"
    print(f"Query: Index of node '{node}'? ->", index[node])

if __name__ == "__main__":
    main() 