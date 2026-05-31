"""
Critic Agent
=============
Fact-checks the research memo and decides if it's ready.
Can loop back to Synthesizer with feedback for rewrites.
"""
import os
from dotenv import load_dotenv
load_dotenv()

from langchain_groq import ChatGroq
from backend.state import AgentState


LLM = ChatGroq(model="llama-3.1-8b-instant", temperature=0)


def critic_agent(state: AgentState) -> dict:
    """
    Evaluates the draft memo for quality and factual accuracy.
    
    Reads: draft_memo, iterations
    Writes: critic_feedback, critic_approved, iterations
    """
    draft_memo = state.get("draft_memo", "")
    iterations = state.get("iterations", 0)
    ticker = state.get("ticker", "UNKNOWN")

    if not draft_memo:
        return {
            "critic_feedback": "No memo to review",
            "critic_approved": False,
            "iterations": iterations,
        }

    prompt = f"""You are a critical fact-checker for investment research memos.
Review this research memo for {ticker} and decide if it meets publication standards.

Evaluate:
1. Is it factually grounded (claims backed by data)?
2. Does it follow the required structure?
3. Is the thesis clear and compelling?
4. Any contradictions or unsupported claims?

Respond with:
- VERDICT: [APPROVE / REVISE]
- FEEDBACK: [specific issues if any, or "Ready for publication"]

Memo to review:
---
{draft_memo}
---

EVALUATION:"""

    response = LLM.invoke(prompt)
    evaluation = response.content.strip()

    verdict = "APPROVE" if "APPROVE" in evaluation.upper() else "REVISE"
    approved = verdict == "APPROVE"

    print(f"[Critic] Iteration {iterations + 1}: {verdict}")
    print(f"  Feedback: {evaluation[:100]}...")

    return {
        "critic_feedback": evaluation,
        "critic_approved": approved,
        "iterations": iterations + 1,
    }


if __name__ == "__main__":
    print("=" * 70)
    print("Testing Full Pipeline: Data -> Specialists -> Synthesizer -> Critic")
    print("=" * 70)

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

    print("\n[1/6] Data Collection...")
    test_state.update(data_collector_agent(test_state))

    print("\n[2-5/6] Specialist Analysis (parallel)...")
    test_state.update(financial_analyst_agent(test_state))
    test_state.update(sentiment_analyst_agent(test_state))
    test_state.update(risk_analyst_agent(test_state))
    test_state.update(peer_analyst_agent(test_state))

    print("\n[6/6] Synthesis & Critique...")
    test_state.update(synthesizer_agent(test_state))

    loop_count = 0
    max_loops = 2
    while loop_count < max_loops:
        test_state.update(critic_agent(test_state))
        loop_count += 1

        if test_state["critic_approved"]:
            print(f"  ✅ Approved after {loop_count} review(s)")
            test_state["final_memo"] = test_state["draft_memo"]
            break
        elif loop_count < max_loops:
            print(f"  -> Loing back to Synthesizer for revision...")
            test_state.update(synthesizer_agent(test_state))
        else:
            print(f"  ⚠️ Max iterations reached, publishing anyway")
            test_state["final_memo"] = test_state["draft_memo"]

    print("\n" + "=" * 70)
    print("FINAL RESEARCH MEMO (first 300 chars):")
    print("=" * 70)
    print(test_state["final_memo"][:300] + "...")
    print("\n" + "=" * 70)
    print(f"Memo length: {len(test_state['final_memo'])} chars")
    print(f"Critic iterations: {test_state['iterations']}")
    print(f"Approved: {test_state['critic_approved']}")
    print("=" * 70)
