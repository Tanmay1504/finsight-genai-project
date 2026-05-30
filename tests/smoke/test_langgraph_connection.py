"""
Smoke test: Verifies LangGraph + Groq connection works.

Not part of production code - just a sanity check that can be run
manually to confirm the environment is properly configured.

Usage:
    python -m tests.smoke.test_langgraph_connection
"""
import os
from dotenv import load_dotenv
load_dotenv()

from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_groq import ChatGroq


class HelloState(TypedDict):
    input_text: str
    output_text: str


def greeting_agent(state):
    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)
    response = llm.invoke("Give me a one-sentence enthusiastic greeting based on: " + state["input_text"])
    return {"output_text": response.content}


graph = StateGraph(HelloState)
graph.add_node("greeter", greeting_agent)
graph.add_edge(START, "greeter")
graph.add_edge("greeter", END)
app = graph.compile()


if __name__ == "__main__":
    print("Running LangGraph connection smoke test...")
    print("=" * 60)
    result = app.invoke({"input_text": "user just built an MCP server with 5 tools"})
    print("")
    print("Agent output:")
    print("   " + result["output_text"])
    print("")
    print("=" * 60)
    print("LangGraph is working!")
