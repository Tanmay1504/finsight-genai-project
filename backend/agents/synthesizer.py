"""
Synthesizer Agent (Enhanced)
============================
Combines all specialist analyses into a polished research memo.
Now includes explicit Critic requirements upfront.
"""
import os
from dotenv import load_dotenv
load_dotenv()

from langchain_anthropic import ChatAnthropic
from backend.state import AgentState


LLM = ChatAnthropic(model="claude-opus-4-6", temperature=0)


def synthesizer_agent(state: AgentState) -> dict:
    """Combines all specialist analyses into a polished research memo."""
    ticker = state.get("ticker", "UNKNOWN")
    financial = state.get("financial_analysis", "No financial analysis available")
    sentiment = state.get("sentiment_analysis", "No sentiment analysis available")
    risk = state.get("risk_analysis", "No risk analysis available")
    peer = state.get("peer_analysis", "No peer analysis available")

    prompt = f"""You are a professional equity research analyst. Write a comprehensive 
research memo for {ticker} that will pass strict fact-checking.

REQUIREMENTS (follow these precisely):
1. FACTUAL GROUNDING: Every claim must be backed by the data provided
2. STRUCTURE: Follow this exact format with clear section headers
3. THESIS CLARITY: State a clear investment recommendation or thesis
4. NO CONTRADICTIONS: Ensure consistency across all sections
5. COMPLETENESS: Address all key dimensions (valuation, growth, risks, competition)

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

Now write the memo. Be comprehensive, factual, and specific."""

    response = LLM.invoke(prompt)
    memo = response.content.strip()
    print(f"[Synthesizer] Memo written ({len(memo)} chars)")
    return {"draft_memo": memo}
