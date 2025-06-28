def main():
    print("\n=== Graph Workflows Demo ===")
    print("Simulating a workflow graph with branching:")
    workflow = {
        "Start": ["Step1"],
        "Step1": ["Step2A", "Step2B"],
        "Step2A": ["End"],
        "Step2B": ["End"],
        "End": []
    }
    print("Nodes:", list(workflow.keys()))
    print("Branches from Step1:", workflow["Step1"])
    print("Path: Start -> Step1 -> Step2A -> End")
    print("Path: Start -> Step1 -> Step2B -> End")

if __name__ == "__main__":
    main() 