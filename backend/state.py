"""
FinSight Agent State Schema
============================
The shared notebook that flows through the multi-agent graph.
Each agent reads what it needs and writes its outputs back.
"""
from typing import Annotated, Optional
from typing_extensions import TypedDict
from operator import add


class AgentState(TypedDict):
    """
    State that flows through the LangGraph multi-agent system.

    Lifecycle:
        1. User provides ticker
        2. Data Collector fills raw_data
        3. Specialists fill their respective analysis fields (in parallel)
        4. Synthesizer produces draft_memo
        5. Critic produces critic_feedback and may loop back to Synthesizer
        6. Once approved, final_memo is set
    """

    # Input
    ticker: str

    # Raw data (filled by Data Collector)
    raw_data: dict

    # Specialist analyses (filled in parallel by 4 agents)
    financial_analysis: Optional[str]
    sentiment_analysis: Optional[str]
    risk_analysis: Optional[str]
    peer_analysis: Optional[str]

    # Synthesizer output
    draft_memo: Optional[str]

    # Critic loop
    critic_feedback: Optional[str]
    critic_approved: Optional[bool]
    iterations: int

    # Fact verification
    fact_issues: Annotated[list, add]

    # Final output
    final_memo: Optional[str]

    # Metadata - parallel agents can append errors here
    errors: Annotated[list, add]
