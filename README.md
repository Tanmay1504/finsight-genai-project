# FinSight Agent

Production-grade autonomous equity research multi-agent system using LangGraph and MCP.

## What is FinSight?

FinSight automates the work of a junior equity research analyst. Enter a stock ticker and receive an institutional-quality research memo in under 90 seconds with every claim source-attributed and fact-checked by a Critic agent.

## Status

- [x] Day 1: MCP Server with 5 financial data tools
- [ ] Day 2: LangGraph multi-agent system
- [ ] Day 3: Critic agent and Evaluator-Optimizer loop
- [ ] Day 4: FastAPI + Streamlit deployment

## Tech Stack

- LangGraph 1.x - Multi-agent orchestration
- FastMCP - Model Context Protocol server
- Pydantic v2 - Data validation
- Groq (Llama 3.3 70B) - LLM inference
- LangSmith - Observability and tracing
- FastAPI - Async backend
- Streamlit - Frontend
- Docker - Containerization
- Render + Streamlit Cloud - Deployment

## MCP Tools

The standalone MCP server (mcp_server/) is compatible with Claude Desktop, ChatGPT, and any MCP-compatible client.

| Tool | Source | Purpose |
|---|---|---|
| stock_overview | Yahoo Finance | Live price, market cap, P/E, sector |
| sec_filings | SEC EDGAR | Official 10-K, 10-Q, 8-K filings |
| earnings_transcript | Tavily | Quarterly earnings call transcripts |
| peer_companies | Curated + Yahoo | Industry competitor benchmarking |
| financial_news | Tavily | Recent financial news (last 30 days) |

## Local Setup

```bash
git clone https://github.com/YOUR_USERNAME/finsight-genai-project.git
cd finsight-genai-project
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys
python -m mcp_server.test_server
```

## Configuration

Required environment variables in .env:

- GROQ_API_KEY
- TAVILY_API_KEY
- LANGSMITH_API_KEY
- LANGSMITH_PROJECT
- LANGSMITH_TRACING
- SEC_USER_AGENT

## License

MIT

## Author

Tanmay Saluja
