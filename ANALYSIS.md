# Application Analysis: website-rag

## System Overview
The current system (`website-rag`) is a **Modular Knowledge Base RAG (Retrieval-Augmented Generation) System**. It allows users to build a persistent database of website content and then query that database using various LLMs.

## Core Workflow
1.  **Indexing Phase (Write):**
    *   User provides a URL.
    *   User selects a **Retrieval Plugin** (Jina or Tavily).
    *   The plugin fetches the content from the URL *at that moment*.
    *   The system processes, chunks, and embeds this content using OpenAI embeddings.
    *   Vectors are stored in **ChromaDB** (persistent storage).
    *   *Note: This snapshot is frozen in time.*

2.  **Query Phase (Read):**
    *   User asks a question.
    *   User selects an **LLM Plugin** (Claude or GPT-4).
    *   The system embeds the question.
    *   The system retrieves relevant chunks **from ChromaDB**.
    *   The system sends chunks + question to the LLM.
    *   *Note: The system DOES NOT access the internet during this phase.*

## Component Analysis

### 1. Data Retrieval (Jina/Tavily)
*   **Function:** Used *exclusively* during the Indexing phase.
*   **Current Behavior:** Fetches content once to populate the database.
*   **Misconception:** The UI dropdown for "Retrieval Engine" during the *Query* phase is misleading. It implies the query will use that engine to search, but the backend currently ignores this selection for retrieval, relying solely on the pre-indexed ChromaDB data.

### 2. Vector Database (ChromaDB)
*   **Function:** The central brain/memory of the application.
*   **Current Behavior:** Stores all indexed content. It does not distinguish *how* the content arrived (via Jina or Tavily); it just stores the text and vectors.
*   **Implication:** If you index with Jina, then query "using Tavily" (in the UI), you are actually querying the Jina-indexed data stored in ChromaDB.

### 3. LLM Generation (Claude/GPT-4)
*   **Function:** Synthesizes answers.
*   **Current Behavior:** Reads the static context retrieved from ChromaDB and generates a response.
*   **Switching:** Switching this component works as expected. You can ask the same question to the same database using different "brains".

## Key Findings & Discrepancies

1.  **Static vs. Dynamic:** The system is built for **Static Knowledge Management** (like a company wiki), not **Dynamic Search** (like Perplexity). It does not support real-time web searching during the query phase.
2.  **UI/Backend Mismatch:** The UI allows selecting a retrieval engine during the query phase, but the backend logic for `/query` does not utilize a retrieval engine—it utilizes the database.
3.  **Persistence:** The Vector DB is **not** recreated every time. It is cumulative. Every time you hit "Index", you add more knowledge. Every time you hit "Ask", you read from that accumulated knowledge.

## Conclusion
The application effectively functions as a "Website-to-Database" converter with a chat interface. It is highly efficient for deep questioning on specific, previously-indexed documentation but is currently incapable of answering questions about real-time events or content that hasn't been explicitly indexed by the user first.
