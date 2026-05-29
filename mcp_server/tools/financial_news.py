"""
Tool: search_financial_news
Searches for recent financial news about a company via Tavily.
"""
import os
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from tavily import TavilyClient

load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")


class NewsArticle(BaseModel):
    title: str = Field(..., description="Article headline")
    url: str = Field(..., description="Article URL")
    published_date: Optional[str] = Field(None, description="Publication date if available")
    snippet: Optional[str] = Field(None, description="Article excerpt/summary")
    score: Optional[float] = Field(None, description="Relevance score")


class FinancialNewsResult(BaseModel):
    ticker: str = Field(..., description="Stock ticker symbol")
    query: str = Field(..., description="Search query used")
    article_count: int = Field(0, description="Number of articles returned")
    articles: list = Field(default_factory=list, description="List of news articles")
    source: str = Field(default="Tavily Search", description="Search provider")
    fetched_at: str = Field(..., description="ISO timestamp")


def search_financial_news(ticker: str, max_results: int = 5) -> dict:
    """
    Search for recent financial news about a company.

    Args:
        ticker: Stock ticker symbol (e.g., "AAPL")
        max_results: Maximum number of articles to return (default: 5)

    Returns:
        Dictionary with list of recent news articles, each containing title,
        URL, snippet, and relevance score.
    """
    ticker = ticker.strip().upper()
    if not ticker:
        raise ValueError("Ticker cannot be empty")
    if not TAVILY_API_KEY:
        raise ValueError("TAVILY_API_KEY not configured in .env")

    # Clamp max_results to a reasonable range
    max_results = max(1, min(int(max_results), 10))

    query = f"{ticker} stock news latest financial"

    try:
        client = TavilyClient(api_key=TAVILY_API_KEY)
        results = client.search(
            query=query,
            max_results=max_results,
            search_depth="advanced",
            topic="news",
            days=30,  # last 30 days
        )

        if not results or not results.get("results"):
            return FinancialNewsResult(
                ticker=ticker,
                query=query,
                article_count=0,
                articles=[],
                fetched_at=datetime.utcnow().isoformat() + "Z",
            ).model_dump()

        articles = []
        for r in results["results"]:
            content = r.get("content") or ""
            snippet = content[:300] + "..." if len(content) > 300 else content
            article = NewsArticle(
                title=r.get("title", ""),
                url=r.get("url", ""),
                published_date=r.get("published_date"),
                snippet=snippet if snippet else None,
                score=r.get("score"),
            )
            articles.append(article.model_dump())

        result = FinancialNewsResult(
            ticker=ticker,
            query=query,
            article_count=len(articles),
            articles=articles,
            fetched_at=datetime.utcnow().isoformat() + "Z",
        )
        return result.model_dump()

    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Failed to fetch news for {ticker}: {str(e)}")


if __name__ == "__main__":
    import json
    result = search_financial_news("AAPL", max_results=3)
    # Truncate snippets for readable print
    for a in result.get("articles", []):
        if a.get("snippet"):
            a["snippet"] = a["snippet"][:150] + "..."
    print(json.dumps(result, indent=2, default=str))
