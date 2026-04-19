# 🔬 Multi-Agent Researcher
### A Self-Correcting AI Research Agent with Reflection Loop

[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://python.org)
[![LangGraph](https://img.shields.io/badge/LangGraph-latest-green)](https://langchain-ai.github.io/langgraph/)
[![Groq](https://img.shields.io/badge/Groq-LLaMA3.3--70b-orange)](https://groq.com)
[![FastAPI](https://img.shields.io/badge/FastAPI-latest-teal)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/Docker-containerized-blue)](https://docker.com)
[![Live Demo](https://img.shields.io/badge/Live-Demo-brightgreen)](https://research-agent-r9fk.onrender.com)

> **Live Demo:** [https://research-agent-r9fk.onrender.com](https://research-agent-r9fk.onrender.com)

---

## 📌 Overview

This project implements a **production-grade multi-agent research system** that mimics a professional research desk. Unlike basic LLM chains, it uses **LangGraph** to create a self-correcting **reflection loop** — if the Fact-Checker agent detects hallucinations or missing sources, the graph cycles back to the Researcher with specific feedback until a quality threshold is met.

Built to demonstrate **senior-level AI engineering concepts** including agentic workflows, human-in-the-loop patterns, observability, and full-stack deployment.

---

## 🏗️ Architecture

```
User Input (Topic)
        │
        ▼
┌─────────────────┐
│   Researcher    │ ◄──────────────────────┐
│     Agent       │                        │
│  (Tavily Web    │                        │ Loop back with
│    Search)      │                        │ specific feedback
└────────┬────────┘                        │
         │                                 │
         ▼                                 │
┌─────────────────┐    Issues Found?       │
│  Fact-Checker   │ ───── YES ─────────────┘
│     Agent       │
│ (Hallucination  │
│   Detection)    │
└────────┬────────┘
         │ Approved (or max 3 iterations)
         ▼
┌─────────────────┐
│    Technical    │
│  Writer Agent   │
│ (Markdown Report│
│  Generation)    │
└────────┬────────┘
         │
         ▼
   Final Report
  (Saved to file
   + API Response)
```

### The Innovation: Reflection Loop

Unlike standard sequential agent chains, this system uses `add_conditional_edges` in LangGraph to create a **feedback cycle**:

- If `quality_approved = True` OR `iteration_count >= 3` → move to Writer
- Otherwise → loop back to Researcher with the Fact-Checker's specific issues

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔄 **Reflection Loop** | Self-correcting agent cycle via LangGraph conditional edges |
| 🌐 **Real Web Search** | Live search via Tavily API with source citation |
| 👤 **Human-in-the-Loop** | CLI mode pauses for human approval before final report |
| 📊 **LangSmith Tracing** | Full observability — traces, token usage, latency per agent |
| ⚡ **FastAPI Backend** | Async REST API with auto-generated Swagger docs |
| 🎨 **Web UI** | Clean dark-mode interface with real-time status updates |
| 🐳 **Dockerized** | Fully containerized for consistent deployment |
| 🚀 **Live Deployment** | Deployed on Render.com with a public URL |

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Agent Framework** | LangGraph |
| **LLM** | Groq (LLaMA 3.3 70b Versatile) |
| **Web Search** | Tavily API |
| **Backend** | FastAPI + Uvicorn |
| **Observability** | LangSmith |
| **Containerization** | Docker |
| **Deployment** | Render.com |

---

## 📁 Project Structure

```
research_agent/
├── .env                    # API keys (never committed)
├── api.py                  # FastAPI backend + Web UI
├── main.py                 # CLI entry point (human-in-the-loop)
├── requirements.txt        # Python dependencies
├── Dockerfile              # Container configuration
├── .dockerignore           # Docker ignore rules
├── graph/
│   ├── __init__.py
│   ├── state.py            # Shared TypedDict state schema
│   ├── nodes.py            # Agent logic (Researcher, FactChecker, Writer)
│   └── graph.py            # LangGraph graph + reflection loop definition
└── tools/
    ├── __init__.py
    └── search.py           # Tavily web search integration
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- API Keys: [Groq](https://console.groq.com) | [Tavily](https://app.tavily.com) | [LangSmith](https://smith.langchain.com)

### 1. Clone the repository

```bash
git clone https://github.com/kaze-ally/research_agent.git
cd research_agent/research_agent
```

### 2. Set up virtual environment

```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the `research_agent/` directory:

```env
GROQ_API_KEY=your_groq_key
TAVILY_API_KEY=your_tavily_key
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_key
LANGCHAIN_PROJECT=multi-agent-researcher
```

### 5. Run the application

**Option A — Web API + UI (recommended):**
```bash
python -m uvicorn api:app --reload --port 8080
```
Open [http://localhost:8080](http://localhost:8080)

**Option B — CLI with Human-in-the-Loop:**
```bash
python main.py
```

---

## 🐳 Docker

### Build the image

```bash
docker build -t researcher-agent .
```

### Run the container

```bash
docker run -p 8080:8080 \
  -e GROQ_API_KEY=your_key \
  -e TAVILY_API_KEY=your_key \
  -e LANGCHAIN_TRACING_V2=true \
  -e LANGCHAIN_API_KEY=your_key \
  -e LANGCHAIN_PROJECT=multi-agent-researcher \
  researcher-agent
```

---

## 📡 API Reference

### `POST /research`

Run the multi-agent research pipeline on a given topic.

**Request:**
```json
{
  "topic": "Latest developments in AI agents 2026"
}
```

**Response:**
```json
{
  "topic": "Latest developments in AI agents 2026",
  "report": "# Latest Developments...\n## Executive Summary\n...",
  "iterations": 3,
  "status": "success"
}
```

### `GET /health`

```json
{
  "status": "online",
  "agent": "multi-agent-researcher"
}
```

### `GET /docs`

Interactive Swagger UI for testing all endpoints.

---

## 🔍 Observability with LangSmith

Every agent run is automatically traced in LangSmith, showing:

- **Token usage** per agent
- **Latency** breakdown across the pipeline
- **Exact prompts** sent to each agent
- **Reflection loop iterations** and feedback cycles

View traces at: [smith.langchain.com](https://smith.langchain.com)

---

## 🧠 Key Concepts Demonstrated

**Self-Correcting Agents** — The Fact-Checker can reject research and send it back with specific feedback, forcing the Researcher to fix exact issues rather than starting from scratch.

**Human-in-the-Loop** — CLI mode uses LangGraph's `MemorySaver` checkpointer with `interrupt_before=["writer"]` to pause execution and await human approval — a critical pattern for production AI systems where full autonomy isn't always desirable.

**State Management** — A `TypedDict` state schema tracks research history, iteration count, quality approval status, and feedback across the entire graph lifecycle.

**Production Observability** — LangSmith integration provides full trace visibility, enabling bottleneck identification and prompt optimization — not just "it works" but *why* it works.

---

## 📈 What This Demonstrates for Interviewers

- ✅ Understanding of **agentic loop patterns** beyond basic chains
- ✅ **Production RAG awareness** — fact-checking, source verification
- ✅ **Safety mindset** — human approval before final output
- ✅ **MLOps skills** — observability, containerization, CI/CD-ready deployment
- ✅ **Full-stack AI** — from LLM to deployed web application

---

## 🗺️ Roadmap

- [ ] Add RAGAS evaluation metrics
- [ ] Streaming API response (real-time token display)
- [ ] Export report as PDF
- [ ] Add memory across research sessions
- [ ] Multi-language report support

---

## 📄 License

MIT License — feel free to use this project as a reference or template.

---

## 🙋 Author

**kaze-ally** — AI Engineering Portfolio Project | 2026

> *"Built a self-correcting multi-agent research system using LangGraph with a reflection loop, human-in-the-loop approval checkpoints, real-time web search via Tavily, and full observability via LangSmith tracing — deployed with FastAPI and Docker."*
