"""
Fact Verifier Agent
====================
Checks memo claims against raw source data.
"""
import os
from dotenv import load_dotenv
load_dotenv()

from langchain_anthropic import ChatAnthropic
from backend.state import AgentState


LLM = ChatAnthropic(model="claude-opus-4-6", temperature=0)


def fact_verifier_agent(state: AgentState) -> dict:
    """Fact-checks memo against raw source data."""
    draft_memo = state.get("draft_memo", "")
    raw_data = state.get("raw_data", {})
    ticker = state.get("ticker", "UNKNOWN")

    if not draft_memo or not raw_data:
        return {"fact_issues": []}

    stock_data = raw_data.get("stock_overview", {})
    peer_data = raw_data.get("peer_companies", {})
    filing_data = raw_data.get("sec_filings", {})
    transcript_data = raw_data.get("earnings_transcript", {})
    news_data = raw_data.get("financial_news", {})

    verification_data = f"""
ACTUAL DATA:
Stock: Price={stock_data.get("current_price")}, MarketCap={stock_data.get("market_cap_formatted")}, PE={stock_data.get("pe_ratio")}, Dividend={stock_data.get("dividend_yield")}
Sector: {stock_data.get("sector")}
Industry: {stock_data.get("industry")}
52w High: {stock_data.get("52_week_high")}, Low: {stock_data.get("52_week_low")}
"""

    prompt = f"""Fact-check this memo against actual source data.
Find ONLY real factual errors (wrong numbers, wrong classifications, contradictions).
Ignore style/structure issues.

Memo:
{draft_memo}

Source Data:
{verification_data}

If facts are accurate, respond: FACTS_VERIFIED
If errors found, list them specifically."""

    response = LLM.invoke(prompt)
    verification = response.content.strip()

    has_issues = "FACTS_VERIFIED" not in verification.upper()

    if has_issues:
        print(f"[Fact Verifier] Issues found: {verification[:100]}...")
    else:
        print(f"[Fact Verifier] OK Facts verified")

    return {"fact_issues": [verification] if has_issues else []}
