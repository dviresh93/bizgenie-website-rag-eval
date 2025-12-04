#!/usr/bin/env python3
"""
Exa.ai Capabilities Demo Script

This script demonstrates Exa.ai's 'search' vs. 'contents' endpoint behavior,
especially concerning non-indexed domains and subpage crawling.

It addresses:
1.  Why Exa's search fails for bizgenieai.com (not indexed).
2.  If Exa's 'contents' endpoint can retrieve content from known URLs.
3.  If Exa's 'contents' endpoint can automatically crawl subpages.
4.  If Exa's 'contents' endpoint can retrieve multiple URLs when explicitly provided.

Usage:
    Ensure EXA_API_KEY environment variable is set.
    Run inside the Docker container for consistent environment:
    docker-compose exec api python3 scripts/exa_capabilities_demo.py
"""
import os
import sys
import time
from exa_py import Exa

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

def run_exa_test():
    api_key = os.getenv("EXA_API_KEY")
    if not api_key:
        print("❌ Error: EXA_API_KEY environment variable not set")
        return

    client = Exa(api_key=api_key)
    
    # --- Test Configuration ---
    target_domains = {
        "BizGenie AI": {
            "root_url": "https://bizgenieai.com",
            "search_query": "What core services does BizGenie provide?",
            "explicit_subpages": [] # No subpages from previous tests
        },
        "Sammamish Chamber": {
            "root_url": "https://sammamishchamber.org/",
            "search_query": "What are the events hosted by Sammamish Chamber?",
            "explicit_subpages": [
                "https://sammamishchamber.org/explore/",
                "https://sammamishchamber.org/explore/about-sammamish/"
            ]
        }
    }
    
    print("="*80)
    print("🕷️  Exa.ai Capabilities Demonstration")
    print("="*80)

    for name, config in target_domains.items():
        root_url = config["root_url"]
        search_query = config["search_query"]
        explicit_subpages = config["explicit_subpages"]

        print(f"\n{'='*70}")
        print(f"Testing Domain: {name} ({root_url})")
        print(f"{'='*70}")

        # --- Test 1: Search Endpoint (Expected to Fail for Non-Indexed Sites) ---
        print("\n1. Testing 'Search' Endpoint (with domain filter)...")
        try:
            response = client.search_and_contents(
                search_query,
                include_domains=[root_url.replace("https://", "").replace("/", "")], # Format for Exa
                num_results=5,
                type="neural",
                text=True
            )
            if response.results:
                print(f"   ⚠️  Unexpectedly found {len(response.results)} search results.")
                for res in response.results:
                    print(f"     - {res.url}")
            else:
                print("   ✅ As expected: 0 search results (domain likely not indexed).")
        except Exception as e:
            print(f"   ❌ Error during search: {e}")

        # --- Test 2: Single Page Retrieval via 'Contents' Endpoint ---
        print("\n2. Testing 'Contents' Endpoint (Single URL Retrieval)...")
        try:
            response = client.get_contents(
                [root_url],
                text=True,
                livecrawl="always"
            )
            if response.results:
                print(f"   ✅ Success! Retrieved main page content.")
                print(f"   Title: {response.results[0].title}")
                print(f"   URL: {response.results[0].url}")
                print(f"   Length: {len(response.results[0].text)} chars")
            else:
                print("   ❌ Failed to retrieve single page content.")
        except Exception as e:
            print(f"   ❌ Error retrieving single page: {e}")

        # --- Test 3: Auto-Crawl via 'Contents' Endpoint (with subpages parameter) ---
        print("\n3. Testing 'Contents' Endpoint (Auto-crawl with subpages=5)...")
        try:
            response = client.get_contents(
                [root_url],
                text=True,
                subpages=5,
                livecrawl="always"
            )
            if len(response.results) > 1:
                print(f"   ⚠️  Unexpectedly retrieved {len(response.results)} results (auto-crawl might work for some sites).")
                for res in response.results:
                    print(f"     - {res.url}")
            else:
                print(f"   ✅ As expected: Only retrieved {len(response.results)} result(s). Auto-crawl did not pick up subpages.")
                if response.results:
                    print(f"     - {response.results[0].url}")
        except Exception as e:
            print(f"   ❌ Error during auto-crawl: {e}")

        # --- Test 4: Explicit List Retrieval via 'Contents' Endpoint ---
        if explicit_subpages:
            print("\n4. Testing 'Contents' Endpoint (Explicit List of URLs Retrieval)...")
            all_urls_to_retrieve = [root_url] + explicit_subpages
            try:
                response = client.get_contents(
                    all_urls_to_retrieve,
                    text=True,
                    livecrawl="always"
                )
                if len(response.results) == len(all_urls_to_retrieve):
                    print(f"   ✅ Success! Retrieved all {len(response.results)}/{len(all_urls_to_retrieve)} requested pages.")
                    for res in response.results:
                        print(f"     - {res.url} (Title: {res.title})")
                elif response.results:
                    print(f"   ⚠️  Partial success. Retrieved {len(response.results)}/{len(all_urls_to_retrieve)} requested pages.")
                    for res in response.results:
                        print(f"     - {res.url} (Title: {res.title})")
                else:
                    print(f"   ❌ Failed to retrieve any pages from explicit list.")
            except Exception as e:
                print(f"   ❌ Error during explicit list retrieval: {e}")
        else:
            print("\n4. Skipping 'Explicit List Retrieval' (no subpages provided for this domain).")

    print(f"\n{'='*80}")
    print("Exa.ai Demo Complete. Review results above.")
    print("="*80)

if __name__ == "__main__":
    run_exa_test()
