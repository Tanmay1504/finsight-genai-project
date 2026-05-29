"""
Tool: get_stock_overview
Fetches current stock data from Yahoo Finance via yfinance.
"""
from datetime import datetime
from typing import Optional
import yfinance as yf
from pydantic import BaseModel, Field


class StockOverview(BaseModel):
    """Structured output for stock overview data."""
    ticker: str = Field(..., description="Stock ticker symbol")
    company_name: Optional[str] = Field(None, description="Full company name")
    current_price: Optional[float] = Field(None, description="Current stock price in USD")
    market_cap: Optional[int] = Field(None, description="Market cap in USD")
    market_cap_formatted: Optional[str] = Field(None, description="Human-readable market cap")
    pe_ratio: Optional[float] = Field(None, description="Trailing P/E ratio")
    dividend_yield: Optional[float] = Field(None, description="Dividend yield as decimal")
    fifty_two_week_high: Optional[float] = Field(None, description="52-week high price")
    fifty_two_week_low: Optional[float] = Field(None, description="52-week low price")
    sector: Optional[str] = Field(None, description="Business sector")
    industry: Optional[str] = Field(None, description="Industry classification")
    summary: Optional[str] = Field(None, description="Business summary")
    source: str = Field(default="Yahoo Finance", description="Data source")
    fetched_at: str = Field(..., description="ISO timestamp of data fetch")


def _format_market_cap(value: Optional[int]) -> Optional[str]:
    """Convert 3245000000000 -> '$3.25T' for human readability."""
    if value is None:
        return None
    if value >= 1_000_000_000_000:
        return f"${value / 1_000_000_000_000:.2f}T"
    elif value >= 1_000_000_000:
        return f"${value / 1_000_000_000:.2f}B"
    elif value >= 1_000_000:
        return f"${value / 1_000_000:.2f}M"
    return f"${value:,}"


def get_stock_overview(ticker: str) -> dict:
    """
    Fetch stock overview data for a given ticker.

    Args:
        ticker: Stock ticker symbol (e.g., "AAPL", "TSLA")

    Returns:
        Dictionary with stock overview data.

    Raises:
        ValueError: If ticker is invalid or no data is available.
    """
    ticker = ticker.strip().upper()

    if not ticker:
        raise ValueError("Ticker cannot be empty")

    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        if not info or len(info) < 5:
            raise ValueError(f"No data found for ticker '{ticker}'. Is it valid?")

        market_cap = info.get("marketCap")

        overview = StockOverview(
            ticker=ticker,
            company_name=info.get("longName") or info.get("shortName"),
            current_price=info.get("currentPrice") or info.get("regularMarketPrice"),
            market_cap=market_cap,
            market_cap_formatted=_format_market_cap(market_cap),
            pe_ratio=info.get("trailingPE"),
            dividend_yield=info.get("dividendYield"),
            fifty_two_week_high=info.get("fiftyTwoWeekHigh"),
            fifty_two_week_low=info.get("fiftyTwoWeekLow"),
            sector=info.get("sector"),
            industry=info.get("industry"),
            summary=info.get("longBusinessSummary"),
            fetched_at=datetime.utcnow().isoformat() + "Z",
        )

        return overview.model_dump()

    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Failed to fetch data for {ticker}: {str(e)}")


if __name__ == "__main__":
    import json
    for tkr in ["AAPL", "TSLA", "MSFT"]:
        print(f"\n{'=' * 60}")
        print(f"Testing: {tkr}")
        print('=' * 60)
        try:
            result = get_stock_overview(tkr)
            print(json.dumps(result, indent=2, default=str))
        except ValueError as e:
            print(f"Error: {e}")
