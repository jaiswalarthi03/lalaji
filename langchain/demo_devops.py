import subprocess

def try_run(cmd):
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"{cmd[0]} output: {result.stdout.strip()}")
        else:
            print(f"{cmd[0]} error: {result.stderr.strip()}")
    except Exception as e:
        print(f"{cmd[0]} not available: {e}")

def main():
    print("\n=== DevOps Demo ===")
    print("Checking pre-commit version...")
    try_run(["pre-commit", "--version"])
    print("Checking Makefile (make --version)...")
    try_run(["make", "--version"])
    print("Checking Docker version...")
    try_run(["docker", "--version"])
    print("(CI/CD pipeline simulation omitted)")

if __name__ == "__main__":
    main() 