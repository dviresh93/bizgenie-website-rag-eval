"""
Test script for Jina plugin and document processing pipeline.
"""
import sys
sys.path.insert(0, '/home/virus/Documents/repo/bizgenie/website-rag')

from api.app.plugins.data_retrieval.jina_plugin import JinaPlugin
from api.app.services.document_processor import DocumentProcessor
import os

def test_jina_pipeline():
    """Test the complete pipeline: fetch -> process -> store"""

    print("=" * 60)
    print("Testing Jina Plugin + Document Processing Pipeline")
    print("=" * 60)

    # Step 1: Initialize Jina plugin
    print("\n[1/5] Initializing Jina plugin...")
    jina_config = {"options": {"batch_size": 5}}
    jina = JinaPlugin(jina_config)
    print("✓ Jina plugin initialized")

    # Step 2: Fetch a URL
    print("\n[2/5] Fetching URL with Jina...")
    test_url = "https://example.com"
    doc = jina.fetch_url(test_url)
    print(f"✓ Fetched: {doc.url}")
    print(f"✓ Content length: {len(doc.content)} characters")
    print(f"✓ Source plugin: {doc.source_plugin}")
    print(f"✓ Preview: {doc.content[:200]}...")

    # Step 3: Initialize document processor
    print("\n[3/5] Initializing document processor...")

    # Check for OpenAI API key
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        print("⚠ OPENAI_API_KEY not set - creating mock processor")
        print("   To test fully: export OPENAI_API_KEY=your-key")
        return

    processor_config = {
        "chunking": {
            "chunk_size": 500,
            "chunk_overlap": 50
        },
        "embedding": {
            "model": "text-embedding-3-small",
            "api_key": openai_key
        },
        "storage": {
            "host": os.getenv("CHROMA_HOST", "localhost"),
            "port": int(os.getenv("CHROMA_PORT", 8001))
        }
    }

    processor = DocumentProcessor(processor_config)
    print("✓ Document processor initialized")

    # Step 4: Process and store
    print("\n[4/5] Processing and storing document...")
    stats = processor.process_and_store([doc], collection_name="test_collection")
    print(f"✓ Processed {stats['documents_processed']} documents")
    print(f"✓ Created {stats['total_chunks']} chunks")
    print(f"✓ Stored in collection: {stats['collection_name']}")

    # Step 5: Test retrieval
    print("\n[5/5] Testing retrieval...")
    query = "What is this website about?"
    results = processor.retrieve(query, collection_name="test_collection", n_results=3)
    print(f"✓ Retrieved {len(results['documents'])} relevant chunks")
    print("\nTop result:")
    print(f"  Content: {results['documents'][0][:150]}...")
    print(f"  Source: {results['metadatas'][0]['url']}")
    print(f"  Distance: {results['distances'][0]:.4f}")

    print("\n" + "=" * 60)
    print("✓ PIPELINE TEST COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    test_jina_pipeline()
