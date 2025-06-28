def calculator(a, b):
    return a + b

def main():
    print("\n=== Custom Tools Demo ===")
    print("Registering custom tool: calculator(a, b)")
    a, b = 2, 2
    print(f"Calling calculator({a}, {b})...")
    result = calculator(a, b)
    print(f"Result: {result}")

if __name__ == "__main__":
    main() 