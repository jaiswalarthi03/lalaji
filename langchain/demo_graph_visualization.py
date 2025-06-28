def main():
    print("\n=== Graph Visualization Demo ===")
    print("Visualizing a simple in-memory graph:")
    graph = {"A": ["B"], "B": ["C", "D"], "C": [], "D": []}
    print("ASCII Art:")
    print("A --> B --> C")
    print("      |\n      v")
    print("      D")

if __name__ == "__main__":
    main() 