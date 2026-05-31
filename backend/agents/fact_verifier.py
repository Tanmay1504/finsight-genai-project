"""
Fact Verifier Agent
====================
Checks memo claims against raw source data.
Identifies factual issues for Synthesizer to fix.
"""
import os
from dotenv import load_dotenv
load_dotenv()

from langchain_groq import ChatGroq
from backend.state import AgentState


LLM = ChatGroq(model="llama-3.1-8b-instant", temperature=0)


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
        print(f"[Fact Verifier] ✅ Facts verified")

    return {"fact_issues": [verification] if has_issues else []}


if __name__ == "__in__":
    from backend.agents.data_collector import data_collector_agent
    from backend.agents.specialists import (
        financial_analyst_agent,
        sentiment_analyst_agent,
        risk_analyst_agent,
        peer_analyst_agent,
    )
    from backend.agents.synthesizer import synthesizer_agent

    test_state = {
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

    print("[1/7] Data Collection...")
    test_state.update(data_collector_agent(test_state))
    print("[2-5/7] Specialists...")
    test_state.update(financial_analyst_agent(test_state))
    test_state.update(sentiment_analyst_agent(test_state))
    test_state.update(risk_analyst_agent(test_state))
    test_state.update(peer_analyst_agent(test_state))
    print("[6/7] Synthesizer...")
    test_state.update(synthesizer_agent(test_state))
    print("[7/7] Fact Verification...")
    test_state.update(fact_verifier_agent(test_state))

    if test_state["fact_issues"]:
        print(f"Issues: {len(test_state['fact_issues'])}")
    else:
        print("✅ All facts verified!")
