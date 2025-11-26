import requests
import sys

BASE_URL = "http://localhost:8000/api/v1"
HEALTH_URL = "http://localhost:8000/health"

def test_endpoints():
    print("Running API Endpoint Tests...")
    
    # 1. Health Check
    try:
        print(f"GET {HEALTH_URL}")
        r = requests.get(HEALTH_URL)
        r.raise_for_status()
        assert r.json() == {"status": "healthy"}
        print("✅ Health check passed")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        sys.exit(1)

    # 2. Index URL
    try:
        print(f"POST {BASE_URL}/index")
        payload = {"url": "https://example.com"}
        r = requests.post(f"{BASE_URL}/index", json=payload)
        r.raise_for_status()
        data = r.json()
        assert data["success"] is True
        print(f"✅ Indexing passed (Collection: {data['collection_name']})")
    except Exception as e:
        print(f"❌ Indexing failed: {e}")
        sys.exit(1)

    # 3. Query
    try:
        print(f"POST {BASE_URL}/query")
        payload = {"question": "What is this domain for?"}
        r = requests.post(f"{BASE_URL}/query", json=payload)
        r.raise_for_status()
        data = r.json()
        print(f"Answer: {data['answer']}")
        assert len(data["answer"]) > 0
        assert data["model_used"] is not None
        print("✅ Query passed")
    except Exception as e:
        print(f"❌ Query failed: {e}")
        sys.exit(1)

    print("\n🎉 All tests passed!")

if __name__ == "__main__":
    test_endpoints()
