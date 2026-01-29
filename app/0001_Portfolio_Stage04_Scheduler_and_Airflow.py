
# ---

# ## How to Use:

# 1. **Place `utils/stock_data.py`** in your `utils/` folder
# 2. **Place `0003_Stock_Selection_Stock_Screener.py`** in your `app/` folder
# 3. Your `streamlit_app.py` will auto-discover it as a new page

# ## Features:

# ✅ **Tab 1 - Index Browser:**
# - Dropdown with 10+ indices (NIFTY 50, BANK, IT, PHARMA, FMCG, etc.)
# - MultiSelect stocks from index (max 10 at a time)
# - Live prices, P/E, dividend yield
# - Expandable detailed metrics (RSI, MA, 52-week range)

# ✅ **Tab 2 - Quick Commodities:**
# - COMEX Gold/Silver prices
# - USD/INR, CAD/INR live rates
# - NIFTY 50, SENSEX live values

# ✅ **Tab 3 - Add to Watchlist:**
# - Manual CSV input
# - Export entire index as CSV
# - Selective stock export
# - Download ready-made CSVs for Stage 02

# ## Reusable Structure:
# - `utils/stock_data.py` has ALL stock lists → easy to update
# - Use `indicators` module from previous files
# - Consistent with your Stage 01 & Stage 02 architecture



# Stock Selection Module


# New Files for Stock Selection Module

## 1. `utils/stock_data.py` - Reusable stock lists

# """
# utils/stock_data.py

# Stock and Index Data Management
# - Comprehensive NSE index list
# - Stock symbols for each index
# - Commodity tickers (Gold, Silver, Forex pairs)
# - All reusable across app modules
# """

# Major NSE Indices with their components
 
## 2. `app/0003_Stock_Selection_Stock_Screener.py` - Main stock selection module

# """
# 0003_Stock_Selection_Stock_Screener.py

# Stock Screener & Selection Module
# - Browse NSE indices and their stocks
# - MultiSelect stocks from indices
# - Add to watchlist
# - Quick commodity/forex prices
# - Export selected stocks as CSV
# """

import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime
from utils import stock_data
from utils import indicators

st.set_page_config(
    page_title="Stock Selection & Screener",
    page_icon="🔎",
    layout="wide"
)

st.title("🔎 Stock Selection & Screener")
st.markdown("**Browse Indices → Select Stocks → Add to Watchlist**")

# ============================================================================
# TABS
# ============================================================================

tab1, tab2, tab3 = st.tabs(["📊 Index Browser", "🏆 Quick Commodities", "📥 Add to Watchlist"])

# ========================== TAB 1: INDEX BROWSER ===========================
with tab1:
    st.header("📊 Browse NSE Indices & Select Stocks")
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        selected_index = st.selectbox(
            "Choose an Index",
            stock_data.get_all_indices(),
            help="Select an NSE index to view its stocks"
        )
    
    with col2:
        st.info(f"ℹ️ Selected: **{selected_index}**")
    
    # Get stocks for selected index
    stocks = stock_data.get_stocks_for_index(selected_index)
    
    if stocks:
        st.subheader(f"📋 Stocks in {selected_index} ({len(stocks)} total)")
        
        # MultiSelect stocks
        selected_stocks = st.multiselect(
            f"Select stocks to analyze (or add to watchlist)",
            stocks,
            max_selections=10,
            help="Choose up to 10 stocks at a time"
        )
        
        if selected_stocks:
            st.success(f"✅ Selected {len(selected_stocks)} stocks")
            
            # Fetch live data for selected stocks
            st.info("🔄 Fetching live data...")
            
            selected_data = []
            progress_bar = st.progress(0)
            
            for i, ticker in enumerate(selected_stocks):
                try:
                    stock = yf.Ticker(ticker)
                    hist = stock.history(period="5d")
                    info = stock.info
                    
                    if not hist.empty:
                        current_price = hist['Close'].iloc[-1]
                        prev_close = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
                        day_change_pct = ((current_price - prev_close) / prev_close * 100) if prev_close > 0 else 0
                        
                        selected_data.append({
                            'Symbol': ticker,
                            'Price': current_price,
                            'Day Change %': day_change_pct,
                            'P/E': info.get('trailingPE'),
                            'Div Yield %': info.get('dividendYield', 0) * 100 if info.get('dividendYield') else 0,
                            'Market Cap': info.get('marketCap'),
                        })
                except Exception:
                    pass
                
                progress_bar.progress(min((i + 1) / len(selected_stocks), 1.0))
            
            if selected_data:
                df_selected = pd.DataFrame(selected_data)
                progress_bar.progress(100)
                st.success(f"✅ Fetched data for {len(df_selected)} stocks")
                
                # Display table
                st.subheader("📈 Live Prices & Metrics")
                st.dataframe(
                    df_selected,
                    column_config={
                        "Price": st.column_config.NumberColumn("Price", format="₹%.2f"),
                        "Day Change %": st.column_config.NumberColumn("Change %", format="%.2f%%"),
                        "P/E": st.column_config.NumberColumn("P/E", format="%.2f"),
                        "Div Yield %": st.column_config.NumberColumn("Yield %", format="%.2f%%"),
                    },
                    use_container_width=True,
                    hide_index=True
                )
                
                # Quick analysis for each stock
                if st.checkbox("📊 Show detailed metrics"):
                    for ticker in selected_stocks:
                        with st.expander(f"📌 {ticker} - Details"):
                            col1, col2, col3 = st.columns(3)
                            
                            try:
                                stock = yf.Ticker(ticker)
                                ind = indicators.calculate_all_indicators(stock)
                                info = stock.info
                                
                                with col1:
                                    st.metric("Price", f"₹{ind['history']['Close'].iloc[-1]:.2f}")
                                    st.metric("P/E", f"{info.get('trailingPE', 'N/A')}")
                                
                                with col2:
                                    st.metric("RSI (14)", f"{ind['rsi']:.0f}" if ind['rsi'] else "N/A")
                                    st.metric("52w High", f"₹{info.get('fiftyTwoWeekHigh', 'N/A'):.2f}")
                                
                                with col3:
                                    st.metric("MA50", f"₹{ind['ma50']:.2f}" if ind['ma50'] else "N/A")
                                    st.metric("52w Low", f"₹{info.get('fiftyTwoWeekLow', 'N/A'):.2f}")
                            
                            except Exception as e:
                                st.error(f"Error fetching details: {e}")
            else:
                st.warning("❌ Could not fetch data for selected stocks")
    else:
        st.warning("⚠️ No stocks found for this index")

# ===================== TAB 2: QUICK COMMODITIES ==========================
with tab2:
    st.header("🏆 Commodities & Forex Prices")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("💰 Precious Metals")
        try:
            gold = yf.Ticker("GC=F").history(period="1d")
            if not gold.empty:
                st.metric("COMEX Gold", f"${gold['Close'].iloc[-1]:,.2f}/oz")
            
            silver = yf.Ticker("SI=F").history(period="1d")
            if not silver.empty:
                st.metric("COMEX Silver", f"${silver['Close'].iloc[-1]:,.2f}/oz")
        except Exception:
            st.warning("Could not fetch metal prices")
    
    with col2:
        st.subheader("💵 Forex Rates")
        try:
            usd_inr = yf.Ticker("INR=X").history(period="1d")
            if not usd_inr.empty:
                st.metric("USD/INR", f"₹{usd_inr['Close'].iloc[-1]:.2f}")
            
            cad_inr = yf.Ticker("CADINR=X").history(period="1d")
            if not cad_inr.empty:
                st.metric("CAD/INR", f"₹{cad_inr['Close'].iloc[-1]:.2f}")
        except Exception:
            st.warning("Could not fetch forex rates")
    
    with col3:
        st.subheader("📊 Indices")
        try:
            nifty = yf.Ticker("^NSEI").history(period="1d")
            if not nifty.empty:
                st.metric("NIFTY 50", f"{nifty['Close'].iloc[-1]:,.0f}")
            
            sensex = yf.Ticker("^BSESN").history(period="1d")
            if not sensex.empty:
                st.metric("SENSEX", f"{sensex['Close'].iloc[-1]:,.0f}")
        except Exception:
            st.warning("Could not fetch index prices")

# ==================== TAB 3: ADD TO WATCHLIST ===========================
with tab3:
    st.header("📥 Add Stocks to Watchlist")
    
    st.info("ℹ️ Use this section to quickly create a CSV file for your watchlist")
    
    # Input method
    method = st.radio("Choose input method:", ["Manual Entry", "Paste from Index"])
    
    if method == "Manual Entry":
        stocks_text = st.text_area(
            "Enter stock symbols (one per line, with or without .NS suffix)",
            height=200,
            help="Example:\nRELIANCE\nTCS.NS\nHDFCBANK"
        )
        
        if stocks_text:
            stocks_list = [s.strip().upper() for s in stocks_text.split('\n') if s.strip()]
            
            if stocks_list:
                st.success(f"✅ Found {len(stocks_list)} stocks")
                
                # Display as DataFrame
                df = pd.DataFrame(stocks_list, columns=['Ticker'])
                st.dataframe(df, use_container_width=True, hide_index=True)
                
                # Download as CSV
                csv = df.to_csv(index=False, header=False)
                st.download_button(
                    label="📥 Download as CSV",
                    data=csv,
                    file_name=f"watchlist_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    key="manual_download"
                )
    
    else:  # Paste from Index
        st.subheader("Select Index & Export Stocks")
        
        index_for_export = st.selectbox(
            "Choose index to export",
            stock_data.get_all_indices(),
            key="export_index"
        )
        
        export_stocks = stock_data.get_stocks_for_index(index_for_export)
        
        if export_stocks:
            st.success(f"✅ {index_for_export} has {len(export_stocks)} stocks")
            
            # Option to select subset
            col1, col2 = st.columns(2)
            
            with col1:
                export_all = st.checkbox(
                    "Export all stocks from this index",
                    value=True
                )
            
            with col2:
                if not export_all:
                    selected_for_export = st.multiselect(
                        "Or select specific stocks",
                        export_stocks
                    )
                    export_stocks = selected_for_export
            
            if export_stocks:
                # Display
                df_export = pd.DataFrame(export_stocks, columns=['Ticker'])
                st.dataframe(df_export, use_container_width=True, hide_index=True)
                
                # Download as CSV
                csv = df_export.to_csv(index=False, header=False)
                st.download_button(
                    label="📥 Download as CSV",
                    data=csv,
                    file_name=f"{index_for_export.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    key="index_download"
                )

# Footer
st.divider()
st.caption(f"✅ Stock Selection & Screener | Indices: {len(stock_data.get_all_indices())} | Stocks: {len(stock_data.get_all_stocks())} | {datetime.now().strftime('%H:%M:%S')}")