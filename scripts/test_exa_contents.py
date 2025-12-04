#!/usr/bin/env python3
"""
Test Exa.ai 'Contents' Endpoint for Crawling
Tests if Exa can retrieve a specific URL and its subpages.
"""
import os
import sys
import json
from exa_py import Exa

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

def test_exa_crawling():
    api_key = os.getenv("EXA_API_KEY")
    if not api_key:
        print("❌ Error: EXA_API_KEY environment variable not set")
        return

    client = Exa(api_key=api_key)
    target_url = "https://sammamishchamber.org/"
    subpages = [
        "https://sammamishchamber.org/explore/",
        "https://sammamishchamber.org/explore/about-sammamish/"
    ]
    
    print("="*60)
    print(f"🕷️  Testing Exa.ai Contents & Crawling for: {target_url}")
    print("="*60)

    # Test 1: Auto-crawl Retrieval
    print("\n1. Testing Auto-crawl (subpages=5)...")
    try:
        response = client.get_contents(
            [target_url],
            text=True,
            subpages=5,
            livecrawl="always"
        )
        if len(response.results) > 1:
            print(f"   ✅ Success! Retrieved {len(response.results)} results.")
            for res in response.results:
                print(f"     - {res.url} ({len(res.text)} chars)")
        else:
            print(f"   ⚠️  Only retrieved {len(response.results)} result(s). Auto-crawl did not pick up subpages.")
            if response.results:
                 print(f"     - {response.results[0].url}")

    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Test 2: Explicit List Retrieval
    print("\n2. Testing Explicit List Retrieval (3 URLs)...")
    all_urls = [target_url] + subpages
    try:
        response = client.get_contents(
            all_urls,
            text=True,
            livecrawl="always"
        )
        
        if response.results:
            print(f"   ✅ Success! Retrieved {len(response.results)}/{len(all_urls)} requested pages.")
            for res in response.results:
                print(f"     - {res.url} (Title: {res.title})")
        else:
            print("   ❌ No results returned.")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Test 3: Single Subpage Retrieval
    print("\n3. Testing Single Subpage Retrieval...")
    subpage_url = "https://sammamishchamber.org/explore/"
    try:
        response = client.get_contents(
            [subpage_url],
            text=True,
            livecrawl="always"
        )
        if response.results:
            print(f"   ✅ Success! Retrieved subpage.")
            print(f"   Title: {response.results[0].title}")
            print(f"   URL: {response.results[0].url}")
        else:
            print("   ❌ Failed to retrieve subpage.")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    test_exa_crawling()