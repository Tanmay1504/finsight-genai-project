"""
Synthesizer Agent
==================
Combines all specialist analyses into a single research memo.
"""
import os
from dotenv import load_dotenv
load_dotenv()

from langchain_groq import ChatGroq
from backend.state import AgentState


LLM = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)


def synthesizer_agent(state: AgentState) -> dict:
    """
    Combines all specialist analyses into a polished research memo.
    
    Reads: financial_analysis, sentiment_analysis, risk_analysis, peer_analysis
    Writes: draft_memo
    """
    ticker = state.get("ticker", "UNKNOWN")
    financial = state.get("financial_analysis", "No financial analysis available")
    sentiment = state.get("sentiment_analysis", "No sentiment analysis available")
    risk = state.get("risk_analysis", "No risk analysis available")
    peer = state.get("peer_analysis", "No peer analysis available")

    prompt = f"""You are a professional equity research analyst at a major investment bank.
Your job is to synthesize the following four specialist analyses into a single, 
cohesive research memo for {ticker}. Write as if this memo will be sent to institutional investors.

Structure your memo with these sections:
1. EXECUTIVE SUMMARY (2 paragraphs)
2. FINANCIAL ANALYSIS
3. SENTIMENT & MANAGEMENT OUTLOOK
4. RISK ASSESSMENT
5. COMPETITIVE POSITIONING
6. INVESTMENT THESIS (concluding paragraph)

Keep the memo professional, concise, and actionable.

=== FINANCIAL ANALYSIS ===
{financial}

=== SENTIMENT ANALYSIS ===
{sentiment}

=== RISK ANALYSIS ===
{risk}

=== PEER ANALYSIS ===
{peer}

=== RESEARCH MEMO ===
"""

    response = LLM.invoke(prompt)
    memo = response.content.strip()

    print(f"[Synthesizer] Memo written ({len(memo)} chars)")
    return {"draft_memo": memo}


if __name__ == "__main__":
    # Standalone test
    print("=" * 70)
    print("Testing Synthesizer Agent")
    print("=" * 70)

    from backend.agents.data_collector import data_collector_agent
    from backend.agents.specialists import (
        financial_analyst_agent,
        sentiment_analyst_agent,
        risk_analyst_agent,
        peer_analyst_agent,
    )

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

    print("\n[1/3] Collecting data...")
    data_result = data_collector_agent(test_state)
    test_state.update(data_result)

    print("\n[2/3] Running specialists...")
    test_state.update(financial_analyst_agent(test_state))
    test_state.update(sentiment_analyst_agent(test_state))
    test_state.update(risk_analyst_agent(test_state))
    test_state.update(peer_analyst_agent(test_state))

    print("\n[3/3] Synthesizing memo...")
    test_state.update(synthesizer_agent(test_state))

    print("\n" + "=" * 70)
    print("RESEARCH MEMO (first 500 chars):")
    print("=" * 70)
    print(test_state["draft_memo"][:500] + "...")
    print("\n" + "=" * 70)
    print(f"Full memo: {len(test_state['draft_memo'])} chars")
    print("=" * 70)
