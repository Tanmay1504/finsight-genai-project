"""
Synthesizer Agent (Enhanced)
============================
Combines all specialist analyses into a polished research memo.
Now includes explicit requirements so it gets Critic approval on first try.
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
    Now includes explicit Critic requirements upfront.
    
    Reads: financial_analysis, sentiment_analysis, risk_analysis, peer_analysis
    Writes: draft_memo
    """
    ticker = state.get("ticker", "UNKNOWN")
    financial = state.get("financial_analysis", "No financial analysis available")
    sentiment = state.get("sentiment_analysis", "No sentiment analysis available")
    risk = state.get("risk_analysis", "No risk analysis available")
    peer = state.get("peer_analysis", "No peer analysis available")

    prompt = f"""You are a professional equity research analyst. Write a comprehensive 
research memo for {ticker} that will pass strict fact-checking.

REQUIREMENTS (these will be evaluated by a Critic, so follow them precisely):
1. FACTUAL GROUNDING: Every claim must be backed by the data provided
2. STRUCTURE: Follow this exact format with clear section headers
3. THESIS CLARITY: State a clear investment recommendation or thesis
4. NO CONTRADICTIONS: Ensure consistency across all sections
5. COMPLETENESS: Address all key dimensions (valuation, growth, risks, competition)
6. CITATIONS: Reference the specific analyst insights from the data provided

Structure your memo EXACTLY like this:

=== RESEARCH MEMO: {ticker} ===

EXECUTIVE SUMMARY
[2 paragraphs covering: company description, key investment thesis, valuation signal]

FINANCIAL ANALYSIS
[Use specific metrics from financial data: P/E, market cap, dividend yield, 52-week range]
[Include valuation assessment: Is it expensive, fair, cheap?]

SENTIMENT & MANAGEMENT OUTLOOK
[From earnings call: What is management confident about?]
[What risks did management highlight?]
[Forward guidance assessment]

RISK ASSESSMENT
[Top 3 critical risks from 10-K filing]
[How do these compare to peer risk profiles?]
[Mitigation factors if any]

COMPETITIVE POSITIONING
[Vs peers: market share, valuation, growth rate]
[Competitive advantages: brand, products, scale]
[Vulnerabilities vs competitors]

INVESTMENT THESIS
[Clear conclusion: BUY / HOLD / SELL rationale]
[Target thesis based on valuation and growth]
[Key catalysts or concerns]

=== FINANCIAL DATA PROVIDED ===
{financial}

=== SENTIMENT ANALYSIS PROVIDED ===
{sentiment}

=== RISK ANALYSIS PROVIDED ===
{risk}

=== COMPETITIVE ANALYSIS PROVIDED ===
{peer}

Now write the memo. Be comprehensive, factual, and specific. Every statement should be 
traceable to the data provided above.
"""

    response = LLM.invoke(prompt)
    memo = response.content.strip()

    print(f"[Synthesizer] Memo written ({len(memo)} chars)")
    return {"draft_memo": memo}


if __name__ == "__main__":
    # Standalone test
    print("=" * 70)
    print("Testing Enhanced Synthesizer (explicit Critic requirements)")
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
    test_state.update(data_collector_agent(test_state))

    print("\n[2/3] Running specialists...")
    test_state.update(financial_analyst_agent(test_state))
    test_state.update(sentiment_analyst_agent(test_state))
    test_state.update(risk_analyst_agent(test_state))
    test_state.update(peer_analyst_agent(test_state))

    print("\n[3/3] Synthesizing memo with Critic requirements built-in...")
    test_state.update(synthesizer_agent(test_state))

    print("\n" + "=" * 70)
    print("ENHANCED MEMO (first 500 chars):")
    print("=" * 70)
    print(test_state["draft_memo"][:500] + "...")
    print("\n" + "=" * 70)
    print(f"Full memo: {len(test_state['draft_memo'])} chars")
    print("=" * 70)
