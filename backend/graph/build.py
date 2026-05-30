"""
LangGraph Builder - Complete 3-Gate Pipeline
Data -> Specialists -> Synthesizer -> Fact Verifier -> Critic -> Final Memo
"""
import os
from dotenv import load_dotenv
load_dotenv()

from backend.state import AgentState
from backend.agents.data_collector import data_collector_agent
from backend.agents.specialists import (
    financial_analyst_agent,
    sentiment_analyst_agent,
    risk_analyst_agent,
    peer_analyst_agent,
)
from backend.agents.synthesizer import synthesizer_agent
from backend.agents.fact_verifier import fact_verifier_agent
from backend.agents.critic import critic_agent


def build_research_graph():
    def run_research_pipeline(ticker: str) -> dict:
        print("=" * 70)
        print(f"FinSight Research Pipeline: {ticker}")
        print("=" * 70)

        state = {
            "ticker": ticker,
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
            "fact_issues": [],
        }

        print("\n[1/7] Data Collection...")
        state.update(data_collector_agent(state))

        print("\n[2-5/7] Specialist Analysis...")
        state.update(financial_analyst_agent(state))
        state.update(sentiment_analyst_agent(state))
        state.update(risk_analyst_agent(state))
        state.update(peer_analyst_agent(state))

        print("\n[6/7] Synthesis...")
        state.update(synthesizer_agent(state))

        print("\n[7a/7] Fact Verification (Gate 1)...")
        for _ in range(2):
            state.update(fact_verifier_agent(state))
            if not state["fact_issues"]:
                print("  OK Facts verified")
                break
            print("  -> Looping back to Synthesizer...")
            state.update(synthesizer_agent(state))

        print("\n[7b/7] Critic Review (Gate 2)...")
        for _ in range(2):
            state.update(critic_agent(state))
            if state["critic_approved"]:
                print("  OK APPROVED")
                state["final_memo"] = state["draft_memo"]
                break
            print("  -> Looping back to Synthesizer...")
            state.update(synthesizer_agent(state))
        else:
            state["final_memo"] = state["draft_memo"]

        print("\n" + "=" * 70)
        print("COMPLETE")
        print("=" * 70)
        print(f"Memo: {len(state['final_memo'])} chars")
        print(f"Approved: {state['critic_approved']}")
        print("=" * 70)

        return state

    return run_research_pipeline


if __name__ == "__main__":
    pipeline = build_research_graph()
    result = pipeline("AAPL")
    print("\nFirst 400 chars of final memo:")
    print("-" * 70)
    print(result["final_memo"][:400] + "...")
