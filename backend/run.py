"""
FinSight Backend Entry Point
=============================
Run as: python -m backend.run AAPL
"""
import sys
from backend.graph.build import build_research_graph


def main():
    if len(sys.argv) < 2:
        print("Usage: python -m backend.run <TICKER>")
        print("Example: python -m backend.run AAPL")
        sys.exit(1)

    ticker = sys.argv[1].upper()
    
    # Build and run the pipeline
    pipeline = build_research_graph()
    result = pipeline(ticker)
    
    # Print the final memo
    print("\n" + "=" * 70)
    print(f"RESEARCH MEMO: {ticker}")
    print("=" * 70 + "\n")
    print(result["final_memo"])
    print("\n" + "=" * 70)
    print("END OF MEMO")
    print("=" * 70)


if __name__ == "__main__":
    main()
