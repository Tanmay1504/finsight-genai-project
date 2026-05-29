"""
Self-test for the MCP server - validates all 5 tools.
"""
import asyncio
from fastmcp import Client
from mcp_server.server import mcp


async def main():
    print("=" * 70)
    print("FINSIGHT MCP SERVER - FULL TEST SUITE")
    print("=" * 70)

    async with Client(mcp) as client:
        tools = await client.list_tools()
        print(f"\nServer has {len(tools)} tool(s):")
        for tool in tools:
            desc = (tool.description or "").strip().split("\n")[0][:80]
            print(f"   - {tool.name}: {desc}")

        # Test 1
        print(f"\n{'=' * 70}\nTEST 1: stock_overview('AAPL')\n{'=' * 70}")
        r = await client.call_tool("stock_overview", {"ticker": "AAPL"})
        d = r.data
        print(f"  Company: {d.get('company_name')}")
        print(f"  Price: ${d.get('current_price')}")
        print(f"  Market Cap: {d.get('market_cap_formatted')}")
        print(f"  P/E: {d.get('pe_ratio')}")

        # Test 2
        print(f"\n{'=' * 70}\nTEST 2: sec_filings('AAPL', '10-K')\n{'=' * 70}")
        r = await client.call_tool("sec_filings", {"ticker": "AAPL", "filing_type": "10-K"})
        d = r.data
        print(f"  Filing: {d.get('filing_type')} | Length: {d.get('full_text_length')} chars")

        # Test 3
        print(f"\n{'=' * 70}\nTEST 3: earnings_transcript('AAPL')\n{'=' * 70}")
        r = await client.call_tool("earnings_transcript", {"ticker": "AAPL"})
        d = r.data
        print(f"  Quarter: {d.get('quarter')}")
        print(f"  Length: {d.get('full_length')} chars")

        # Test 4
        print(f"\n{'=' * 70}\nTEST 4: peer_companies('AAPL')\n{'=' * 70}")
        r = await client.call_tool("peer_companies", {"ticker": "AAPL"})
        d = r.data
        print(f"  Sector: {d.get('sector')} | Peers: {d.get('peer_count')}")
        for p in d.get('peers', []):
            print(f"    - {p.get('ticker')}: {p.get('company_name')} ({p.get('market_cap_formatted')})")

        # Test 5
        print(f"\n{'=' * 70}\nTEST 5: financial_news('AAPL', max_results=3)\n{'=' * 70}")
        r = await client.call_tool("financial_news", {"ticker": "AAPL", "max_results": 3})
        d = r.data
        print(f"  Articles found: {d.get('article_count')}")
        for a in d.get('articles', []):
            print(f"    - {a.get('title', '')[:80]}")
            print(f"      {a.get('url', '')[:80]}")

        print(f"\n{'=' * 70}")
        print("ALL 5 TOOLS PASSED")
        print('=' * 70)


if __name__ == "__main__":
    asyncio.run(main())
