"""
Critic Agent (Smarter Version)
==============================
Evaluates memo based on structure, completeness, and coherence.
"""
import os
from dotenv import load_dotenv
load_dotenv()

from langchain_anthropic import ChatAnthropic
from backend.state import AgentState


LLM = ChatAnthropic(model="claude-opus-4-6", temperature=0)


def critic_agent(state: AgentState) -> dict:
    """Evaluates the draft memo for publication readiness."""
    draft_memo = state.get("draft_memo", "")
    iterations = state.get("iterations", 0)
    ticker = state.get("ticker", "UNKNOWN")

    if not draft_memo:
        return {
            "critic_feedback": "No memo to review",
            "critic_approved": False,
            "iterations": iterations,
        }

    prompt = f"""You are a publication editor for investment research.
Evaluate if this memo is ready for publication.

Check:
1. STRUCTURE: Does it have all required sections?
2. CLARITY: Is the thesis clear and understandable?
3. COMPLETENESS: Does it address valuation, growth, risks, competition?
4. COHERENCE: Are there contradictions or confusing statements?

Decision: APPROVE or NEEDS_WORK

Memo:
---
{draft_memo}
---

DECISION:"""

    response = LLM.invoke(prompt)
    evaluation = response.content.strip()

    verdict = "APPROVE" if "APPROVE" in evaluation.upper() else "NEEDS_WORK"
    approved = verdict == "APPROVE"

    print(f"[Critic] Iteration {iterations + 1}: {verdict}")
    if not approved:
        print(f"  Feedback: {evaluation[:150]}...")

    return {
        "critic_feedback": evaluation,
        "critic_approved": approved,
        "iterations": iterations + 1,
    }
