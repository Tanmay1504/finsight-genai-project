"""
Data Collector Agent
=====================
Calls all FinSight MCP tools in parallel and stuffs the results into State.
This is the bridge between LangGraph (brain) and MCP server (toolbox).
"""
import asyncio
from fastmcp import Client
from mcp_server.server import mcp

from backend.state import AgentState


async def _call_all_tools(ticker: str) -> tuple[dict, list]:
    """
    Call all 5 MCP tools in parallel for the given ticker.
    Returns (raw_data_dict, errors_list).
    """
    raw_data = {}
    errors = []

    async with Client(mcp) as client:
        # Define the tool calls we want to make
        tool_calls = [
            ("stock_overview", {"ticker": ticker}),
            ("sec_filings", {"ticker": ticker, "filing_type": "10-K"}),
            ("earnings_transcript", {"ticker": ticker}),
            ("peer_companies", {"ticker": ticker}),
            ("financial_news", {"ticker": ticker, "max_results": 5}),
        ]

        # Fire all tool calls in parallel via asyncio.gather
        async def call_one(tool_name, args):
            try:
                result = await client.call_tool(tool_name, args)
                return tool_name, result.data, None
            except Exception as e:
                return tool_name, None, f"{tool_name} failed: {str(e)}"

        results = await asyncio.gather(
            *[call_one(name, args) for name, args in tool_calls]
        )

        # Collect results
        for tool_name, data, error in results:
            if error:
                errors.append(error)
            else:
                raw_data[tool_name] = data

    return raw_data, errors


def data_collector_agent(state: AgentState) -> dict:
    """
    LangGraph node: collects all data from MCP tools.

    Reads:  state["ticker"]
    Writes: state["raw_data"], state["errors"]
    """
    ticker = state["ticker"]
    print(f"[Data Collector] Fetching all data for {ticker}...")

    # Run the async function in a sync context (LangGraph nodes can be sync)
    raw_data, errors = asyncio.run(_call_all_tools(ticker))

    # Report what we got
    tools_succeeded = list(raw_data.keys())
    print(f"[Data Collector] Successful: {tools_succeeded}")
    if errors:
        print(f"[Data Collector] Errors: {len(errors)}")

    return {
        "raw_data": raw_data,
        "errors": errors,
    }


if __name__ == "__main__":
    # Standalone test
    import json

    print("=" * 70)
    print("Testing Data Collector Agent")
    print("=" * 70)

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

    result = data_collector_agent(test_state)

    print("\nSummary of collected data:")
    print("-" * 70)
    for tool_name, data in result["raw_data"].items():
        if isinstance(data, dict):
            keys = list(data.keys())[:5]
            print(f"  {tool_name}: {len(data)} fields - sample keys: {keys}")
        else:
            print(f"  {tool_name}: {type(data).__name__}")

    if result["errors"]:
        print(f"\nErrors: {result['errors']}")
    else:
        print("\nNo errors. Data Collector working correctly.")
