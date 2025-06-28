import requests
import re

def get_title(url):
    try:
        resp = requests.get(url, timeout=5)
        if resp.ok:
            m = re.search(r'<title>(.*?)</title>', resp.text, re.IGNORECASE)
            if m:
                return m.group(1)
        return None
    except Exception:
        return None

def main():
    print("\n=== Docs & Demos Demo ===")
    url = "https://api.langchain.com"
    print(f"API Reference: {url}")
    title = get_title(url)
    if title:
        print(f"Title: {title}")
    else:
        print("(Could not fetch title)")
    print("Tutorials: https://docs.langchain.com/tutorials")
    print("Guides: https://docs.langchain.com/guides")
    print("Cookbook: https://github.com/langchain-ai/langchain/tree/master/cookbook")

if __name__ == "__main__":
    main() 