"""
Tool: get_earnings_transcript
Fetches recent earnings call transcripts via Tavily search.
"""
import os
import re
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from tavily import TavilyClient

load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")


class EarningsTranscript(BaseModel):
    ticker: str = Field(..., description="Stock ticker symbol")
    company_name: Optional[str] = Field(None, description="Company name")
    quarter: Optional[str] = Field(None, description="Quarter referenced")
    source_url: Optional[str] = Field(None, description="URL of the transcript source")
    source_title: Optional[str] = Field(None, description="Title of source page")
    transcript_excerpt: Optional[str] = Field(None, description="Excerpt of transcript text")
    full_length: int = Field(0, description="Length of fetched content")
    source: str = Field(default="Tavily Search", description="Search provider")
    fetched_at: str = Field(..., description="ISO timestamp")


def _extract_quarter(text):
    if not text:
        return None
    match = re.search(r"\b(Q[1-4])\s*(\d{4})\b", text)
    if match:
        return f"{match.group(1)} {match.group(2)}"
    match = re.search(r"\b(first|second|third|fourth)\s+quarter\s+(?:of\s+)?(\d{4})", text, re.IGNORECASE)
    if match:
        q_map = {"first": "Q1", "second": "Q2", "third": "Q3", "fourth": "Q4"}
        return f"{q_map[match.group(1).lower()]} {match.group(2)}"
    return None


def get_earnings_transcript(ticker: str) -> dict:
    """
    Fetch the most recent earnings call transcript for a ticker.

    Args:
        ticker: Stock ticker symbol (e.g., "AAPL")

    Returns:
        Dictionary with transcript excerpt, source, and metadata.
    """
    ticker = ticker.strip().upper()
    if not ticker:
        raise ValueError("Ticker cannot be empty")
    if not TAVILY_API_KEY:
        raise ValueError("TAVILY_API_KEY not configured in .env")

    try:
        client = TavilyClient(api_key=TAVILY_API_KEY)
        query = f"{ticker} earnings call transcript latest quarter"
        results = client.search(
            query=query,
            max_results=5,
            search_depth="advanced",
            include_raw_content=True,
        )

        if not results or not results.get("results"):
            raise ValueError(f"No earnings transcripts found for {ticker}")

        best = max(
            results["results"],
            key=lambda r: len(r.get("raw_content") or r.get("content") or ""),
        )

        raw_content = best.get("raw_content") or best.get("content") or ""
        cleaned = re.sub(r"\s+", " ", raw_content).strip()
        excerpt = cleaned[:5000] if cleaned else None
        quarter = _extract_quarter(cleaned) or _extract_quarter(best.get("title", ""))

        title = best.get("title", "")
        company_name = None
        if title:
            name_match = re.match(r"^([^(]+?)(?:\s*\([A-Z]{1,5}\))?", title)
            if name_match:
                company_name = name_match.group(1).strip()

        result = EarningsTranscript(
            ticker=ticker,
            company_name=company_name,
            quarter=quarter,
            source_url=best.get("url"),
            source_title=title,
            transcript_excerpt=excerpt,
            full_length=len(cleaned),
            fetched_at=datetime.utcnow().isoformat() + "Z",
        )
        return result.model_dump()

    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Failed to fetch earnings transcript for {ticker}: {str(e)}")


if __name__ == "__main__":
    import json
    result = get_earnings_transcript("AAPL")
    if result.get("transcript_excerpt"):
        result["transcript_excerpt"] = result["transcript_excerpt"][:400] + "..."
    print(json.dumps(result, indent=2, default=str))
