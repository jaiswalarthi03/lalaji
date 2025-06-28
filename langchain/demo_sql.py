import sqlite3

def main():
    print("\n=== SQL Demo ===")
    print("Using in-memory SQLite DB...")
    conn = sqlite3.connect(":memory:")
    c = conn.cursor()
    c.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)")
    c.execute("INSERT INTO users (id, name) VALUES (?, ?)", (1, "Alice"))
    conn.commit()
    c.execute("SELECT name FROM users WHERE id=1;")
    row = c.fetchone()
    print(f"Result: {row[0] if row else 'No result'}")
    conn.close()

if __name__ == "__main__":
    main() 