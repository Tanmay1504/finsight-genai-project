"""
FinSight MCP Server
Provides 5 financial data tools via the Model Context Protocol.
"""
from dotenv import load_dotenv
from fastmcp import FastMCP

from mcp_server.tools.stock_overview import get_stock_overview
from mcp_server.tools.sec_filings import get_sec_filings
from mcp_server.tools.earnings_transcript import get_earnings_transcript
from mcp_server.tools.peer_companies import get_peer_companies
from mcp_server.tools.financial_news import search_financial_news

load_dotenv()


mcp = FastMCP(
    name="FinSight",
    instructions=(
        "FinSight provides real-time financial data and research tools for "
        "equity analysis. Use these tools to fetch stock data, SEC filings, "
        "earnings transcripts, peer comparisons, and recent financial news. "
        "All data is sourced from primary sources (Yahoo Finance, SEC EDGAR, "
        "Tavily) with full source attribution for auditability."
    ),
)


@mcp.tool()
def stock_overview(ticker: str) -> dict:
    """
    Get a comprehensive overview of a publicly traded stock.

    Returns current price, market capitalization, P/E ratio, dividend yield,
    52-week range, sector/industry, and business summary.

    Args:
        ticker: Stock ticker symbol like "AAPL", "TSLA", "MSFT".

    Returns:
        Dictionary with stock data including price, market cap, P/E ratio, etc.
    """
    return get_stock_overview(ticker)


@mcp.tool()
def sec_filings(ticker: str, filing_type: str = "10-K") -> dict:
    """
    Fetch the most recent SEC filing for a company.

    Use for official SEC filings: annual reports (10-K), quarterly reports
    (10-Q), or current event filings (8-K). Returns Risk Factors, MD&A,
    and Business Description excerpts.

    Args:
        ticker: Stock ticker symbol.
        filing_type: "10-K", "10-Q", or "8-K". Default: "10-K"

    Returns:
        Dictionary with filing metadata and key section excerpts.
    """
    return get_sec_filings(ticker, filing_type)


@mcp.tool()
def earnings_transcript(ticker: str) -> dict:
    """
    Fetch the most recent earnings call transcript for a company.

    Earnings calls happen quarterly. The transcript contains management
    commentary on results, forward guidance, and Q&A with analysts.
    Critical for sentiment analysis.

    Args:
        ticker: Stock ticker symbol.

    Returns:
        Dictionary with transcript excerpt, source URL, quarter, and metadata.
    """
    return get_earnings_transcript(ticker)


@mcp.tool()
def peer_companies(ticker: str) -> dict:
    """
    Get peer (competitor) companies for a given ticker.

    Returns competitors in the same industry with their key metrics
    (market cap, price, P/E ratio) for comparative analysis.

    Args:
        ticker: Stock ticker symbol.

    Returns:
        Dictionary with sector, industry, and list of peers with their metrics.
    """
    return get_peer_companies(ticker)


@mcp.tool()
def financial_news(ticker: str, max_results: int = 5) -> dict:
    """
    Search for recent financial news about a company.

    Returns news articles from the last 30 days, ranked by relevance.
    Useful for identifying recent events, risks, and market sentiment.

    Args:
        ticker: Stock ticker symbol.
        max_results: Number of articles to return (1-10, default: 5).

    Returns:
        Dictionary with list of news articles (title, URL, snippet, score).
    """
    return search_financial_news(ticker, max_results)


if __name__ == "__main__":
    mcp.run()
