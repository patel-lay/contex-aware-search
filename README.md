
# AI-Powered Document Retrieval System

## Overview
This project implements a **multi-source retrieval-augmented generation (RAG) system** that ingests, embeds, and queries documents from multiple sources (web crawled data, markdown files, and beyond).  

The system uses **PostgreSQL with pgvector** for storage and semantic search, and **FastAPI** to expose a query API. Agents run in parallel across different document sources, and an **aggregator agent** merges results into a unified response with citations.  

---

##  Architecture

### 1. Ingestion
- **Web Crawler** → extracts HTML content, cleans it, splits into sections/chunks, and stores text + citation path.  
- **Markdown Loader** → parses markdown files, splits into chunks, and stores with file path for traceability.  
- Additional sources (PDF, Notion, Confluence, etc.) can be added easily.  

Each chunk is **embedded via Ollama (or any embedding model)** and stored in **Postgres (pgvector)**.  

---

### 2. Storage
- **Postgres + pgvector** is the **system of record**:
  - `doc_type` distinguishes sources (`web`, `markdown`, etc.).  
  - Each row contains `section_id`, `citation`, `chunk_content`, and its `embedding`.  

- **Redis (optional)** acts as a **cache layer**:
  - Store frequent queries or intermediate agent results.  
  - Keep retrieval latency low without duplicating embeddings.  

---

### 3. Retrieval & Agents
- **Parallel Retrieval**:  
  - Agents query different subsets (e.g., web docs vs markdown docs).  
  - Each agent retrieves top-k relevant chunks via vector search.  

- **Aggregator Agent**:  
  - Combines results.  
  - Deduplicates overlapping chunks.  
  - Generates a concise final answer **with citations**.  

---

### 4. Query API
- Exposed via **FastAPI**:  
  - `/query` endpoint accepts a user question.  
  - Internally, dispatches queries to agents in parallel.  
  - Aggregates and returns summarized result with references.  

Example response:
```json
{
  "answer": "Metaflow provides a scalable way to manage ML workflows [Source: https://docs.metaflow.org/introduction].",
  "sources": [
    "https://docs.metaflow.org/introduction",
    "local_docs/guide.md#section-3"
  ]
}
```
### 5. Workflow

- **Ingest Documents**:

    - Web crawler scrapes allowed pages (robots.txt respected).

    - Markdown files parsed.

    - Each split into semantic chunks.

    - Embed + Store

    - Generate embeddings (Ollama, OpenAI, or similar).

    - Insert text + citation + embedding into documents table.

- **Query**:

    - User submits question to API.

    - Agents retrieve chunks from relevant tables/sections.

    - Aggregator agent merges and summarizes with citations.

    - Cache (optional)

    - Redis stores hot queries or agent results.

### 6. Future Improvements:

    - Add more connectors (PDF, Confluence, Slack messages, etc.).

    - Add re-ranking layer for better search quality.

    - Introduce feedback loop to improve retrieval precision.

    - Explore hybrid search (text + embedding).

    - Add observability (latency metrics, retrieval coverage).

### 7. Why This Design?

 - Scalable: pgvector keeps embeddings + metadata in one store.

 - Flexible: agents can be extended to new data sources easily.

 - Reliable: Postgres ensures consistency; Redis provides performance.

 - Transparent: every answer includes citations for traceability.

### 8. Status

MVP Done: Single-document ingestion + retrieval + summarization(using redis as primary database).

Next Steps: Multi-source ingestion → parallel agents → aggregator → citations.

## System Architecture

```mermaid
flowchart TD

    %% Ingestion
    subgraph Ingestion
        A1[Web Crawler] --> A3[Chunk & Embed]
        A2[Markdown Loader] --> A3[Chunk & Embed]
    end

    %% Storage
    subgraph Storage
        B1[(Postgres + pgvector)]
        B2[(Redis Cache)]
    end

    A3 --> B1
    A3 --> B2

    %% Retrieval
    subgraph Retrieval
        C1[Agent: Web Docs]
        C2[Agent: Markdown Docs]
        C3[Aggregator Agent]
    end

    B1 --> C1
    B1 --> C2
    B2 --> C1
    B2 --> C2
    C1 --> C3
    C2 --> C3

    %% API Layer
    subgraph API
        D1[FastAPI /query Endpoint]
    end

    C3 --> D1

    %% User
    U[User] -->|Question| D1
    D1 -->|Answer + Citations| U
