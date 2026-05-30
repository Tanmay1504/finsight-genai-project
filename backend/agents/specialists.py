"""
Specialist Analyst Agents
==========================
Four parallel agents that analyze raw data using the LLM.

- Financial Analyst: analyzes stock metrics, market cap, P/E, etc.
- Sentiment Analyst: analyzes earnings call tone and management outlook
- Risk Analyst: analyzes risk factors from 10-K filing
- Peer Analyst: analyzes competitive position vs peers
"""
import os
from dotenv import load_dotenv
load_dotenv()

from langchain_groq import ChatGroq
from backend.state import AgentState


LLM = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)


# ===== FINANCIAL ANALYST =====
def financial_analyst_agent(state: AgentState) -> dict:
    """Analyzes stock metrics and financial health."""
    raw_data = state.get("raw_data", {})
    stock_data = raw_data.get("stock_overview", {})
    peer_data = raw_data.get("peer_companies", {})

    prompt = f"""You are a financial analyst. Based on this stock data, provide a concise 
financial analysis (2-3 paragraphs) covering:
- Current valuation (P/E, market cap)
- Financial health (dividend yield, 52-week range)
- Competitive positioning vs peers

Stock Data:
{stock_data}

Peer Comparison:
{peer_data}

Analysis:"""

    response = LLM.invoke(prompt)
    analysis = response.content.strip()

    print(f"[Financial Analyst] Analysis complete ({len(analysis)} chars)")
    return {"financial_analysis": analysis}


# ===== SENTIMENT ANALYST =====
def sentiment_analyst_agent(state: AgentState) -> dict:
    """Analyzes earnings call tone and management sentiment."""
    raw_data = state.get("raw_data", {})
    transcript = raw_data.get("earnings_transcript", {})
    quarter = transcript.get("quarter", "Unknown")
    excerpt = transcript.get("transcript_excerpt", "")[:2000]

    prompt = f"""You are a sentiment analyst specializing in earnings calls. 
Analyze the tone and sentiment in this earnings call transcript (quarter: {quarter}).
Provide a 2-3 paragraph analysis covering:
- Overall management tone (confident, cautious, optimistic, etc.)
- Key strategic priorities mentioned
- Growth outlook and forward guidance sentiment

Transcript Excerpt:
{excerpt}

Sentiment Analysis:"""

    response = LLM.invoke(prompt)
    analysis = response.content.strip()

    print(f"[Sentiment Analyst] Analysis complete ({len(analysis)} chars)")
    return {"sentiment_analysis": analysis}


# ===== RISK ANALYST =====
def risk_analyst_agent(state: AgentState) -> dict:
    """Analyzes risk factors from 10-K filing."""
    raw_data = state.get("raw_data", {})
    filing_data = raw_data.get("sec_filings", {})
    risk_excerpt = filing_data.get("risk_factors_excerpt", "")[:2000]

    prompt = f"""You are a risk analyst. Based on the risk factors from the company's 10-K filing,
provide a 2-3 paragraph risk assessment covering:
- Top 3 critical risks to the business
- Regulatory or competitive threats
- Financial or operational vulnerabilities

Risk Factors (10-K):
{risk_excerpt}

Risk Analysis:"""

    response = LLM.invoke(prompt)
    analysis = response.content.strip()

    print(f"[Risk Analyst] Analysis complete ({len(analysis)} chars)")
    return {"risk_analysis": analysis}


# ===== PEER ANALYST =====
def peer_analyst_agent(state: AgentState) -> dict:
    """Analyzes competitive position vs peers."""
    raw_data = state.get("raw_data", {})
    stock_data = raw_data.get("stock_overview", {})
    peer_data = raw_data.get("peer_companies", {})

    prompt = f"""You are a competitive analyst. Analyze this company's position vs peers.
Provide a 2-3 paragraph analysis covering:
- Market share and competitive advantages
- Valuation vs peer group (P/E, market cap)
- Growth trajectory and market positioning

Company (Stock Overview):
{stock_data}

Peer Group Data:
{peer_data}

Competitive Analysis:"""

    response = LLM.invoke(prompt)
    analysis = response.content.strip()

    print(f"[Peer Analyst] Analysis complete ({len(analysis)} chars)")
    return {"peer_analysis": analysis}


if __name__ == "__main__":
    # Standalone test
    print("=" * 70)
    print("Testing Specialist Agents (requires raw_data from Data Collector)")
    print("=" * 70)

    from backend.agents.data_collector import data_collector_agent

    test_state: AgentState = {
        "ticker": "AAPL",
        "raw_data": {},
        "financial_analysis": None,
        "sentiment_analysis": None,
        "risk_analysis": None,
        "peer_analysis": None,
        "draft_memo": None,
        "critic_feedback": None,
        "critic_approved": None,
        "iterations": 0,
        "final_memo": None,
        "errors": [],
    }

    print("\n[1/2] Collecting data...")
    data_result = data_collector_agent(test_state)
    test_state.update(data_result)

    print("\n[2/2] Running specialist agents in parallel...")
    print("-" * 70)

    # In real LangGraph, these run in parallel. For testing, we run sequentially.
    fin_result = financial_analyst_agent(test_state)
    sent_result = sentiment_analyst_agent(test_state)
    risk_result = risk_analyst_agent(test_state)
    peer_result = peer_analyst_agent(test_state)

    test_state.update(fin_result)
    test_state.update(sent_result)
    test_state.update(risk_result)
    test_state.update(peer_result)

    print("\n" + "=" * 70)
    print("All specialist analyses complete!")
    print("=" * 70)
    print(f"Financial Analysis: {len(test_state['financial_analysis'])} chars")
    print(f"Sentiment Analysis: {len(test_state['sentiment_analysis'])} chars")
    print(f"Risk Analysis: {len(test_state['risk_analysis'])} chars")
    print(f"Peer Analysis: {len(test_state['peer_analysis'])} chars")
