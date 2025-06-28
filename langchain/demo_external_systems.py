import requests

def main():
    print("\n=== External Systems Demo ===")
    print("Calling external API: httpbin.org/get ...")
    try:
        resp = requests.get("https://httpbin.org/get", timeout=5)
        if resp.ok:
            data = resp.json()
            print(f"API response: url={data['url']}")
        else:
            print(f"API error: {resp.status_code}")
    except Exception as e:
        print(f"API call failed: {e}")

if __name__ == "__main__":
    main() 