"""
Specialist Analyst Agents
==========================
Four parallel agents that analyze raw data using Claude.
"""
import os
from dotenv import load_dotenv
load_dotenv()

from langchain_anthropic import ChatAnthropic
from backend.state import AgentState


LLM = ChatAnthropic(model="claude-opus-4-6", temperature=0)


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
