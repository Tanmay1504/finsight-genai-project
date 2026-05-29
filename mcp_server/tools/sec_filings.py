"""
Tool: get_sec_filings
Fetches recent SEC filings (10-K, 10-Q) from EDGAR.
"""
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from sec_edgar_downloader import Downloader
from bs4 import BeautifulSoup

load_dotenv()

SEC_USER_AGENT = os.getenv("SEC_USER_AGENT", "FinSight Research research@example.com")
PARTS = SEC_USER_AGENT.rsplit(" ", 1)
USER_NAME = PARTS[0] if len(PARTS) > 1 else "FinSight Research"
USER_EMAIL = PARTS[1] if len(PARTS) > 1 else "research@example.com"

CACHE_DIR = Path("sec-edgar-filings")


class SECFiling(BaseModel):
    ticker: str = Field(..., description="Stock ticker symbol")
    filing_type: str = Field(..., description="Filing type (e.g., '10-K', '10-Q')")
    filing_date: Optional[str] = Field(None, description="Date filed")
    risk_factors_excerpt: Optional[str] = Field(None, description="Risk factors text")
    mdna_excerpt: Optional[str] = Field(None, description="MD&A excerpt")
    business_description: Optional[str] = Field(None, description="Business description")
    full_text_length: int = Field(0, description="Total filing text length")
    source: str = Field(default="SEC EDGAR", description="Data source")
    fetched_at: str = Field(..., description="ISO timestamp")


def _extract_section(text: str, keywords: list, max_chars: int = 3000) -> Optional[str]:
    """Find a section by keyword and return a chunk."""
    text_lower = text.lower()
    for kw in keywords:
        idx = text_lower.find(kw.lower())
        if idx != -1:
            chunk = text[idx:idx + max_chars]
            chunk = re.sub(r'\s+', ' ', chunk).strip()
            return chunk
    return None


def _clean_html(html_content: str) -> str:
    """Strip HTML tags and clean text."""
    soup = BeautifulSoup(html_content, "lxml")
    for tag in soup(["script", "style"]):
        tag.decompose()
    text = soup.get_text(separator=" ")
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def get_sec_filings(ticker: str, filing_type: str = "10-K") -> dict:
    """
    Fetch the most recent SEC filing for a ticker.

    Args:
        ticker: Stock ticker symbol (e.g., "AAPL")
        filing_type: "10-K" (annual), "10-Q" (quarterly), or "8-K" (events)

    Returns:
        Dictionary with filing metadata and key section excerpts.
    """
    ticker = ticker.strip().upper()
    filing_type = filing_type.strip().upper()

    if filing_type not in ("10-K", "10-Q", "8-K"):
        raise ValueError(f"filing_type must be 10-K, 10-Q, or 8-K. Got: {filing_type}")

    if not ticker:
        raise ValueError("Ticker cannot be empty")

    try:
        dl = Downloader(USER_NAME, USER_EMAIL, str(CACHE_DIR))
        dl.get(filing_type, ticker, limit=1, download_details=True)

        filing_dir = CACHE_DIR / "sec-edgar-filings" / ticker / filing_type
        if not filing_dir.exists():
            raise ValueError(f"No {filing_type} filings found for {ticker}")

        filing_folders = sorted(filing_dir.iterdir(), reverse=True)
        if not filing_folders:
            raise ValueError(f"No filing folders for {ticker}")

        latest_folder = filing_folders[0]

        filing_files = (
            list(latest_folder.glob("*.htm"))
            + list(latest_folder.glob("*.html"))
            + list(latest_folder.glob("*.txt"))
        )
        if not filing_files:
            raise ValueError(f"No filing documents in {latest_folder}")

        # Use the largest file (usually the main filing)
        primary_file = max(filing_files, key=lambda p: p.stat().st_size)

        with open(primary_file, "r", encoding="utf-8", errors="ignore") as f:
            raw_content = f.read()

        # Clean HTML if it looks like HTML
        if "<html" in raw_content.lower() or "<HTML" in raw_content:
            text = _clean_html(raw_content)
        else:
            text = re.sub(r'\s+', ' ', raw_content).strip()

        # Extract key sections
        risk_factors = _extract_section(
            text,
            ["Risk Factors", "ITEM 1A", "Item 1A."],
            max_chars=3000
        )
        mdna = _extract_section(
            text,
            ["Management's Discussion and Analysis", "ITEM 7", "Item 7."],
            max_chars=3000
        )
        business_desc = _extract_section(
            text,
            ["Business", "ITEM 1.", "Item 1."],
            max_chars=2000
        )

        # Filing date from folder name (format: ACCESSION-YYYYMMDD)
        folder_name = latest_folder.name
        date_match = re.search(r'(\d{4})(\d{2})(\d{2})', folder_name)
        filing_date = f"{date_match.group(1)}-{date_match.group(2)}-{date_match.group(3)}" if date_match else None

        result = SECFiling(
            ticker=ticker,
            filing_type=filing_type,
            filing_date=filing_date,
            risk_factors_excerpt=risk_factors,
            mdna_excerpt=mdna,
            business_description=business_desc,
            full_text_length=len(text),
            fetched_at=datetime.utcnow().isoformat() + "Z",
        )

        return result.model_dump()

    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Failed to fetch {filing_type} for {ticker}: {str(e)}")


if __name__ == "__main__":
    import json
    result = get_sec_filings("AAPL", "10-K")
    # Truncate long fields for readable print
    for key in ["risk_factors_excerpt", "mdna_excerpt", "business_description"]:
        if result.get(key):
            result[key] = result[key][:300] + "..."
    print(json.dumps(result, indent=2, default=str))
