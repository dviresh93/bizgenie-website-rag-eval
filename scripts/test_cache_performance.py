"""
Focused performance tests for Semantic Cache

Tests:
1. Cold cache (all misses)
2. Warm cache (all exact hits)
3. Semantic matching (similar questions)
4. Mixed workload
"""

import json
import os
import sys
import time
from pathlib import Path

# Add api to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from api.app.services.semantic_cache import SemanticCacheManager
from api.app.tools.jina_tool import JinaTool


def print_section(title):
    """Print a formatted section header."""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def test_cold_cache():
    """Test 1: Cold cache - all queries should miss."""
    print_section("TEST 1: Cold Cache Performance (All Misses)")

    cache = SemanticCacheManager()
    cache.clear_cache()
    cache.reset_stats()

    test_questions = [
        "What services does BizGenie offer?",
        "How much does BizGenie cost?",
        "Does BizGenie integrate with GoHighLevel?",
        "What industries does BizGenie serve?",
        "How does BizGenie handle customer data?"
    ]

    target_url = "https://bizgenieai.com/"

    print(f"\nRunning {len(test_questions)} queries against empty cache...")

    for i, question in enumerate(test_questions, 1):
        cached_result, cache_status, retrieval_time = cache.get_cached_search(
            tool="jina",
            question=question,
            context=target_url
        )

        status_emoji = "❌" if cache_status == "miss" else "✓"
        print(f"  [{i}] {status_emoji} {cache_status}: {retrieval_time*1000:.1f}ms - {question[:50]}...")

    stats = cache.get_stats()
    print(f"\n📊 Results:")
    print(f"   Expected: 100% misses")
    print(f"   Actual: {stats['misses']}/{stats['total_queries']} misses ({stats['misses']/stats['total_queries']*100:.0f}%)")
    print(f"   ✓ PASS" if stats['misses'] == stats['total_queries'] else "   ❌ FAIL")

    return cache


def test_warm_cache(cache: SemanticCacheManager):
    """Test 2: Warm cache - all queries should hit exactly."""
    print_section("TEST 2: Warm Cache Performance (All Exact Hits)")

    # First, populate cache with mock results
    test_questions = [
        "What services does BizGenie offer?",
        "How much does BizGenie cost?",
        "Does BizGenie integrate with GoHighLevel?",
        "What industries does BizGenie serve?",
        "How does BizGenie handle customer data?"
    ]

    target_url = "https://bizgenieai.com/"

    print(f"\nPopulating cache with {len(test_questions)} entries...")

    for question in test_questions:
        mock_result = {
            "content": f"Mock search result for: {question}",
            "sources": ["https://bizgenieai.com"]
        }

        cache.store_search_result(
            tool="jina",
            question=question,
            context=target_url,
            search_result=mock_result,
            search_time=0.5
        )

    # Reset stats before testing
    cache.reset_stats()

    print(f"\nRunning {len(test_questions)} queries against warm cache...")

    exact_hit_times = []

    for i, question in enumerate(test_questions, 1):
        cached_result, cache_status, retrieval_time = cache.get_cached_search(
            tool="jina",
            question=question,
            context=target_url
        )

        if cache_status == "exact_hit":
            exact_hit_times.append(retrieval_time)

        status_emoji = "⚡" if cache_status == "exact_hit" else "❌"
        print(f"  [{i}] {status_emoji} {cache_status}: {retrieval_time*1000:.1f}ms - {question[:50]}...")

    stats = cache.get_stats()

    avg_time = sum(exact_hit_times) / len(exact_hit_times) if exact_hit_times else 0

    print(f"\n📊 Results:")
    print(f"   Expected: 100% exact hits, <30ms average")
    print(f"   Actual: {stats['exact_hits']}/{stats['total_queries']} exact hits ({stats['hit_rate']:.0f}%)")
    print(f"   Avg Retrieval Time: {avg_time*1000:.1f}ms")

    passed = (stats['exact_hits'] == stats['total_queries'] and avg_time < 0.030)
    print(f"   ✓ PASS" if passed else "   ❌ FAIL")

    return cache


def test_semantic_matching(cache: SemanticCacheManager):
    """Test 3: Semantic matching - similar questions should hit."""
    print_section("TEST 3: Semantic Matching (Similar Questions)")

    target_url = "https://bizgenieai.com/"

    # Original questions stored in cache
    original_questions = [
        "What services does BizGenie offer?",
        "How much does BizGenie cost?",
        "Does BizGenie integrate with GoHighLevel?"
    ]

    # Semantically similar variations
    similar_questions = [
        "What does BizGenie provide to businesses?",  # Similar to #1
        "What is the pricing for BizGenie?",  # Similar to #2
        "Can BizGenie connect with GoHighLevel?"  # Similar to #3
    ]

    # Populate cache with original questions
    print(f"\nPopulating cache with {len(original_questions)} original questions...")

    for question in original_questions:
        mock_result = {
            "content": f"Mock answer for: {question}",
            "sources": ["https://bizgenieai.com"]
        }

        cache.store_search_result(
            tool="jina",
            question=question,
            context=target_url,
            search_result=mock_result,
            search_time=0.5
        )

    # Reset stats
    cache.reset_stats()

    print(f"\nTesting {len(similar_questions)} semantically similar queries...")

    semantic_hits = 0
    semantic_hit_times = []

    for i, (original, similar) in enumerate(zip(original_questions, similar_questions), 1):
        cached_result, cache_status, retrieval_time = cache.get_cached_search(
            tool="jina",
            question=similar,
            context=target_url
        )

        if cache_status == "semantic_hit":
            semantic_hits += 1
            semantic_hit_times.append(retrieval_time)
            similarity = cached_result.get("_cache_similarity", 0)
            status_emoji = "⚡"
        else:
            similarity = 0
            status_emoji = "❌"

        print(f"  [{i}] {status_emoji} {cache_status} (sim: {similarity:.3f}): {retrieval_time*1000:.1f}ms")
        print(f"       Original: {original}")
        print(f"       Similar:  {similar}")

    avg_time = sum(semantic_hit_times) / len(semantic_hit_times) if semantic_hit_times else 0

    print(f"\n📊 Results:")
    print(f"   Expected: ≥66% semantic hits, <60ms average")
    print(f"   Actual: {semantic_hits}/{len(similar_questions)} semantic hits ({semantic_hits/len(similar_questions)*100:.0f}%)")
    print(f"   Avg Retrieval Time: {avg_time*1000:.1f}ms")

    passed = (semantic_hits >= 2 and avg_time < 0.060)
    print(f"   ✓ PASS" if passed else "   ❌ FAIL")

    return cache


def test_real_workload():
    """Test 4: Real-world mixed workload."""
    print_section("TEST 4: Real Workload Simulation")

    cache = SemanticCacheManager()
    cache.clear_cache()
    cache.reset_stats()

    # Load actual test questions
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    questions_path = os.path.join(project_root, "config/test_suites/standard_questions.json")

    try:
        with open(questions_path, 'r') as f:
            questions_data = json.load(f)
    except Exception as e:
        print(f"❌ Could not load questions: {e}")
        return

    # Initialize Jina tool
    print("\n🔧 Initializing Jina tool...")
    jina_tool = JinaTool({"api_key_env": "JINA_API_KEY"})

    target_url = "https://bizgenieai.com/"

    # Run 1: Cold cache (first 5 questions)
    print(f"\n🔵 Run 1: Cold Cache (First 5 Questions)")

    for i, q in enumerate(questions_data[:5], 1):
        question_text = q["question"]

        # Check cache
        cached_result, cache_status, cache_time = cache.get_cached_search(
            tool="jina",
            question=question_text,
            context=target_url
        )

        if cached_result:
            print(f"  [{i}] ⚡ {cache_status}: {cache_time*1000:.1f}ms")
        else:
            # Cache miss - perform real search
            start = time.time()
            try:
                search_res = jina_tool.search(question_text, context=target_url)
                search_time = time.time() - start

                # Store in cache
                cached_data = {
                    "content": search_res.content,
                    "sources": search_res.sources
                }

                cache.store_search_result(
                    tool="jina",
                    question=question_text,
                    context=target_url,
                    search_result=cached_data,
                    search_time=search_time
                )

                print(f"  [{i}] 🔍 Real search: {search_time*1000:.0f}ms")
            except Exception as e:
                print(f"  [{i}] ❌ Search failed: {e}")

    # Run 2: Warm cache (same 5 questions)
    print(f"\n🟢 Run 2: Warm Cache (Same 5 Questions)")

    cache.reset_stats()

    for i, q in enumerate(questions_data[:5], 1):
        question_text = q["question"]

        cached_result, cache_status, cache_time = cache.get_cached_search(
            tool="jina",
            question=question_text,
            context=target_url
        )

        status_emoji = "⚡" if cache_status != "miss" else "❌"
        print(f"  [{i}] {status_emoji} {cache_status}: {cache_time*1000:.1f}ms")

    stats = cache.get_stats()

    print(f"\n📊 Warm Cache Results:")
    print(f"   Hit Rate: {stats['hit_rate']:.0f}%")
    print(f"   Avg Exact Retrieval: {stats['avg_exact_retrieval_time']*1000:.1f}ms")

    passed = stats['hit_rate'] == 100
    print(f"   ✓ PASS" if passed else "   ❌ FAIL")


def main():
    """Run all cache performance tests."""
    print("\n" + "🧪"*35)
    print("  SEMANTIC CACHE PERFORMANCE TEST SUITE")
    print("🧪"*35)

    try:
        # Test 1: Cold cache
        cache = test_cold_cache()

        # Test 2: Warm cache
        cache = test_warm_cache(cache)

        # Test 3: Semantic matching
        cache = test_semantic_matching(cache)

        # Test 4: Real workload
        test_real_workload()

        print("\n" + "="*70)
        print("  ✅ ALL TESTS COMPLETE")
        print("="*70 + "\n")

    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
