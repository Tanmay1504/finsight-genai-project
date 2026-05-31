"""
FinSight Frontend - Streamlit UI
==================================
Run as: streamlit run frontend/app.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import streamlit as st
from backend.graph.build import build_research_graph


st.set_page_config(page_title="FinSight", layout="wide")

st.title("📊 FinSight — Autonomous Equity Research Agent")
st.markdown("AI-powered institutional-grade research in 90 seconds")

col1, col2 = st.columns([2, 1])

with col1:
    ticker = st.text_input("Enter stock ticker:", "AAPL", placeholder="AAPL, MSFT, GOOGL, etc.")

with col2:
    generate_button = st.button("🚀 Generate Research", use_container_width=True)

if generate_button:
    if not ticker:
        st.error("Please enter a ticker symbol")
    else:
        st.info(f"🔄 Researching {ticker.upper()}... This takes ~2-3 minutes")
        
        try:
            # Run the pipeline
            pipeline = build_research_graph()
            result = pipeline(ticker.upper())
            
            # Display resul       st.success("✅ Research complete!")
            
            st.markdown("---")
            st.markdown("### 📝 Research Memo")
            st.markdown(result["final_memo"])
            
            st.markdown("---")
            st.markdown("### 📊 Analysis Summary")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Memo Length", f"{len(result['final_memo'])} chars")
            with col2:
                st.metric("Analysis Depth", f"{len(result.get('financial_analysis', ''))} chars")
            with col3:
                status = "✅ Approved" if result.get("critic_approved") else "📋 Published"
                st.metric("Status", status)
                
        except Exception as e:
            st.error(f"Error: {str(e)}")
            st.info("Make sure all API keys are set in .env")

st.markdown("---")
st.markdown("""
### How it works
1. **Data Collection** — Fetches stock data, SEC filings, earnings calls, news
2. **Specialist Analysis**ysts examine from different angles
3. **Synthesis** — Combines into a comprehensive memo
4. **Fact Verification** — Checks claims against source data
5. **Critic Review** — Validates quality and completeness
6. **Publication** — Final memo ready for investors
""")
