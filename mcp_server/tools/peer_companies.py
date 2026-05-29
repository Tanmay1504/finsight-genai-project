"""
Tool: get_peer_companies
Returns peer (competitor) companies in the same industry as the given ticker.
"""
from datetime import datetime
from typing import Optional
import yfinance as yf
from pydantic import BaseModel, Field


# Curated peer groups for major companies - faster and more reliable than scraping
PEER_GROUPS = {
    # Mega-cap tech
    "AAPL": ["MSFT", "GOOGL", "META", "AMZN"],
    "MSFT": ["AAPL", "GOOGL", "ORCL", "AMZN"],
    "GOOGL": ["META", "MSFT", "AAPL", "AMZN"],
    "GOOG": ["META", "MSFT", "AAPL", "AMZN"],
    "META": ["GOOGL", "SNAP", "PINS", "AAPL"],
    "AMZN": ["MSFT", "GOOGL", "WMT", "COST"],
    # Semiconductors
    "NVDA": ["AMD", "INTC", "AVGO", "TSM"],
    "AMD": ["NVDA", "INTC", "AVGO", "QCOM"],
    "INTC": ["AMD", "NVDA", "QCOM", "TSM"],
    "AVGO": ["NVDA", "AMD", "QCOM", "MRVL"],
    "TSM": ["INTC", "NVDA", "AMD", "ASML"],
    # EV & Auto
    "TSLA": ["F", "GM", "RIVN", "LCID"],
    "F": ["GM", "TSLA", "STLA", "TM"],
    "GM": ["F", "TSLA", "STLA", "TM"],
    "RIVN": ["TSLA", "LCID", "F", "GM"],
    # Banks
    "JPM": ["BAC", "WFC", "C", "GS"],
    "BAC": ["JPM", "WFC", "C", "MS"],
    "WFC": ["JPM", "BAC", "C", "USB"],
    "GS": ["MS", "JPM", "BAC", "C"],
    "MS": ["GS", "JPM", "BAC", "C"],
    "C": ["JPM", "BAC", "WFC", "GS"],
    # Indian banks (NSE)
    "HDFCBANK.NS": ["ICICIBANK.NS", "KOTAKBANK.NS", "AXISBANK.NS", "SBIN.NS"],
    "ICICIBANK.NS": ["HDFCBANK.NS", "KOTAKBANK.NS", "AXISBANK.NS", "SBIN.NS"],
    # Streaming / Media
    "NFLX": ["DIS", "WBD", "PARA", "CMCSA"],
    "DIS": ["NFLX", "WBD", "PARA", "CMCSA"],
    # Retail
    "WMT": ["COST", "TGT", "AMZN", "KR"],
    "COST": ["WMT", "TGT", "BJ", "KR"],
    "TGT": ["WMT", "COST", "AMZN", "KR"],
    # Energy
    "XOM": ["CVX", "SHEL", "BP", "TTE"],
    "CVX": ["XOM", "SHEL", "BP", "COP"],
    # Pharma
    "JNJ": ["PFE", "MRK", "ABBV", "LLY"],
    "PFE": ["JNJ", "MRK", "ABBV", "BMY"],
    "LLY": ["JNJ", "MRK", "NVO", "PFE"],
    # Payments
    "V": ["MA", "PYPL", "AXP", "SQ"],
    "MA": ["V", "PYPL", "AXP", "SQ"],
    # Aerospace / Defense
    "BA": ["LMT", "RTX", "NOC", "GD"],
    "LMT": ["RTX", "NOC", "BA", "GD"],
}


class PeerCompany(BaseModel):
    ticker: str = Field(..., description="Peer ticker symbol")
    company_name: Optional[str] = Field(None, description="Peer company name")
    market_cap: Optional[int] = Field(None, description="Market cap")
    market_cap_formatted: Optional[str] = Field(None, description="Formatted market cap")
    current_price: Optional[float] = Field(None, description="Current price")
    pe_ratio: Optional[float] = Field(None, description="P/E ratio")


class PeerCompaniesResult(BaseModel):
    ticker: str = Field(..., description="Original ticker symbol")
    sector: Optional[str] = Field(None, description="Sector of the company")
    industry: Optional[str] = Field(None, description="Industry of the company")
    peers: list = Field(default_factory=list, description="List of peer companies")
    peer_count: int = Field(0, description="Number of peers found")
    source: str = Field(default="Curated + Yahoo Finance", description="Data source")
    fetched_at: str = Field(..., description="ISO timestamp")


def _format_market_cap(value):
    if value is None:
        return None
    if value >= 1_000_000_000_000:
        return f"${value / 1_000_000_000_000:.2f}T"
    elif value >= 1_000_000_000:
        return f"${value / 1_000_000_000:.2f}B"
    elif value >= 1_000_000:
        return f"${value / 1_000_000:.2f}M"
    return f"${value:,}"


def _fetch_peer_summary(ticker):
    """Fetch lightweight summary for a peer ticker."""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        if not info or len(info) < 5:
            return None
        market_cap = info.get("marketCap")
        return PeerCompany(
            ticker=ticker,
            company_name=info.get("longName") or info.get("shortName"),
            market_cap=market_cap,
            market_cap_formatted=_format_market_cap(market_cap),
            current_price=info.get("currentPrice") or info.get("regularMarketPrice"),
            pe_ratio=info.get("trailingPE"),
        ).model_dump()
    except Exception:
        return None


def get_peer_companies(ticker: str) -> dict:
    """
    Get peer (competitor) companies for a given ticker.

    Args:
        ticker: Stock ticker symbol (e.g., "AAPL")

    Returns:
        Dictionary with sector, industry, and list of peer companies with their key metrics.
    """
    ticker = ticker.strip().upper()
    if not ticker:
        raise ValueError("Ticker cannot be empty")

    try:
        # Get the company sector/industry
        stock = yf.Ticker(ticker)
        info = stock.info
        sector = info.get("sector") if info else None
        industry = info.get("industry") if info else None

        # Look up curated peers
        peer_tickers = PEER_GROUPS.get(ticker, [])

        # Fetch summary for each peer
        peers = []
        for pt in peer_tickers:
            peer_data = _fetch_peer_summary(pt)
            if peer_data:
                peers.append(peer_data)

        result = PeerCompaniesResult(
            ticker=ticker,
            sector=sector,
            industry=industry,
            peers=peers,
            peer_count=len(peers),
            fetched_at=datetime.utcnow().isoformat() + "Z",
        )
        return result.model_dump()

    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Failed to fetch peers for {ticker}: {str(e)}")


if __name__ == "__main__":
    import json
    result = get_peer_companies("AAPL")
    print(json.dumps(result, indent=2, default=str))
