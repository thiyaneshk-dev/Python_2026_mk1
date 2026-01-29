"""
0002_Watchlist_Stage02_Watchlist_and_Research.py

Watchlist Management & Research
- Simple CSV: filename.csv with one ticker per line
- Fetch live prices + key metrics (P/E, Dividend Yield, 52-week range)
- Technical indicators (RSI, MA50, MA200)
- Compare vs index performance
- Save watchlist to JSON for persistence
"""

import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# ============================================================================
# CONFIGURATION
# ============================================================================

DATA_DIR = "data"
WATCHLIST_FILE = os.path.join(DATA_DIR, "watchlist_stage02.json")
os.makedirs(DATA_DIR, exist_ok=True)

st.set_page_config(
    page_title="Watchlist Stage 02 - Research & Analysis",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 Watchlist Stage 02 - Research & Analysis")
st.markdown("**Upload CSV → Live Prices → Technical Analysis → Performance Tracking**")

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

@st.cache_data(ttl=300)
def get_stock_data(ticker):
    """Fetch comprehensive stock data from yfinance"""
    if pd.isna(ticker) or not str(ticker).strip():
        return None
    
    ticker_clean = str(ticker).strip()
    
    # Add .NS suffix for common NSE stocks
    if any(kw in ticker_clean.upper() for kw in ['HDFC', 'RELI', 'ITC', 'LICI', 'LUPIN',
                                                    'NIFTY', 'GOLD', 'SILVER', 'LIQUID',
                                                    'GHCL', 'HAPP', 'HINDU', 'PGINVIT', 'TATVA','JUNIORBEES']):
        symbol = f"{ticker_clean}.NS"
    else:
        symbol = ticker_clean
    
    try:
        stock = yf.Ticker(symbol)
        
        # Get historical data for technical indicators
        hist = stock.history(period="200d")  # 200 days for MA200
        
        # Get current info
        info = stock.info
        
        if hist.empty:
            return None
        
        current_price = hist['Close'].iloc[-1]
        
        # Calculate technical indicators
        ma50 = hist['Close'].tail(50).mean() if len(hist) >= 50 else None
        ma200 = hist['Close'].tail(200).mean() if len(hist) >= 200 else None
        
        # RSI calculation (14-period)
        if len(hist) >= 14:
            delta = hist['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            rsi_value = rsi.iloc[-1]
        else:
            rsi_value = None
        
        # 52-week range
        year_hist = stock.history(period="365d")
        if not year_hist.empty:
            high_52w = year_hist['High'].max()
            low_52w = year_hist['Low'].min()
        else:
            high_52w = None
            low_52w = None
        
        return {
            'symbol': symbol,
            'current_price': current_price,
            'ma50': ma50,
            'ma200': ma200,
            'rsi': rsi_value,
            'high_52w': high_52w,
            'low_52w': low_52w,
            'pe_ratio': info.get('trailingPE'),
            'dividend_yield': info.get('dividendYield'),
            'market_cap': info.get('marketCap'),
            'previous_close': info.get('previousClose'),
            'day_change': ((current_price - info.get('previousClose', current_price)) / 
                          info.get('previousClose', current_price) * 100 if info.get('previousClose') else None)
        }
    except Exception:
        return None

def parse_watchlist_csv(uploaded_file):
    """Parse watchlist CSV (simple: one ticker per line)"""
    try:
        df = pd.read_csv(uploaded_file, header=None, names=['ticker'])
        df['ticker'] = df['ticker'].astype(str).str.strip().str.upper()
        df = df[df['ticker'].str.len() > 0].reset_index(drop=True)
        return df
    except Exception as e:
        st.error(f"❌ CSV parsing error: {str(e)}")
        st.error("Expected format: One ticker per line (no header)")
        return pd.DataFrame()

def save_watchlist(watchlist_df):
    """Save watchlist to JSON"""
    watchlist_data = watchlist_df['ticker'].tolist()
    with open(WATCHLIST_FILE, 'w') as f:
        json.dump(watchlist_data, f, indent=2)
    return len(watchlist_data)

def load_watchlist():
    """Load watchlist from JSON"""
    if os.path.exists(WATCHLIST_FILE):
        try:
            with open(WATCHLIST_FILE, 'r') as f:
                data = json.load(f)
            return pd.DataFrame({'ticker': data})
        except Exception:
            return pd.DataFrame()
    return pd.DataFrame()

# ============================================================================
# MAIN UI
# ============================================================================

tab1, tab2, tab3, tab4 = st.tabs(["📁 Upload CSV", "📊 Watchlist View", "📈 Technical Analysis", "📉 Performance"])

with tab1:
    st.header("📁 Upload Watchlist CSV")
    
    uploaded_file = st.file_uploader(
        "Choose CSV file",
        type=['csv'],
        help="Simple format: one ticker per line (e.g., RELIANCE, HDFC, ITC)"
    )
    
    if uploaded_file is not None:
        watchlist_df = parse_watchlist_csv(uploaded_file)
        
        if not watchlist_df.empty:
            st.success(f"✅ Parsed {len(watchlist_df)} tickers")
            
            st.subheader("📋 Preview")
            st.dataframe(
                watchlist_df,
                width='stretch',
                hide_index=True
            )
            
            if st.button("💾 Save Watchlist", type="primary", use_container_width=True):
                count = save_watchlist(watchlist_df)
                st.success(f"✅ Saved {count} tickers!")
                st.balloons()
        else:
            st.error("❌ No valid tickers found in CSV")

with tab2:
    st.header("📊 Watchlist View (Live Prices)")
    
    watchlist_df = load_watchlist()
    
    if watchlist_df.empty:
        st.info("📭 **Upload CSV first** (Tab 1)")
    else:
        st.success(f"📊 {len(watchlist_df)} tickers loaded")
        
        st.info("🔄 Fetching live data...")
        progress_bar = st.progress(0)
        
        # Fetch data for all tickers
        watchlist_data = []
        for i, ticker in enumerate(watchlist_df['ticker']):
            data = get_stock_data(ticker)
            if data:
                watchlist_data.append(data)
            progress_bar.progress(min((i + 1) / len(watchlist_df), 1.0))
        
        if watchlist_data:
            data_df = pd.DataFrame(watchlist_data)
            successful = len(data_df)
            progress_bar.progress(100)
            st.success(f"✅ Fetched data for {successful}/{len(watchlist_df)} tickers")
            
            # Display table
            st.subheader("📋 Live Prices & Metrics")
            
            display_df = data_df[[
                'symbol', 'current_price', 'day_change', 'pe_ratio', 
                'dividend_yield', 'rsi'
            ]].copy()
            
            display_df.columns = ['Symbol', 'Price', 'Day Change %', 'P/E', 'Div Yield %', 'RSI']
            
            st.dataframe(
                display_df,
                column_config={
                    "Price": st.column_config.NumberColumn("Price", format="₹%.2f"),
                    "Day Change %": st.column_config.NumberColumn("Change %", format="%.2f%%"),
                    "P/E": st.column_config.NumberColumn("P/E", format="%.2f"),
                    "Div Yield %": st.column_config.NumberColumn("Yield %", format="%.2f%%"),
                    "RSI": st.column_config.NumberColumn("RSI", format="%.0f"),
                },
                width='stretch',
                hide_index=True
            )
            
            # Summary metrics
            st.subheader("📈 Watchlist Summary")
            col1, col2, col3, col4 = st.columns(4)
            
            avg_pe = data_df['pe_ratio'].mean()
            avg_yield = data_df['dividend_yield'].mean()
            count_positive = (data_df['day_change'] > 0).sum()
            
            with col1:
                st.metric("Total Tickers", len(data_df))
            with col2:
                st.metric("Avg P/E", f"{avg_pe:.2f}" if pd.notna(avg_pe) else "N/A")
            with col3:
                st.metric("Avg Div Yield", f"{avg_yield*100:.2f}%" if pd.notna(avg_yield) else "N/A")
            with col4:
                st.metric("Up Today", f"{count_positive}/{len(data_df)}")
        else:
            st.warning("❌ Could not fetch data for any tickers")

with tab3:
    st.header("📈 Technical Analysis")
    
    watchlist_df = load_watchlist()
    
    if watchlist_df.empty:
        st.info("📭 Upload watchlist first (Tab 1)")
    else:
        # Fetch latest data
        watchlist_data = []
        for ticker in watchlist_df['ticker']:
            data = get_stock_data(ticker)
            if data:
                watchlist_data.append(data)
        
        if watchlist_data:
            data_df = pd.DataFrame(watchlist_data)
            
            # Select ticker for detailed analysis
            selected_ticker = st.selectbox(
                "Select ticker for detailed analysis",
                data_df['symbol'].tolist()
            )
            
            ticker_data = data_df[data_df['symbol'] == selected_ticker].iloc[0]
            
            st.subheader(f"🔍 {selected_ticker} - Detailed Analysis")
            
            # Metrics
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.metric("Price", f"₹{ticker_data['current_price']:.2f}")
            with col2:
                st.metric("P/E Ratio", f"{ticker_data['pe_ratio']:.2f}" if pd.notna(ticker_data['pe_ratio']) else "N/A")
            with col3:
                st.metric("RSI (14)", f"{ticker_data['rsi']:.0f}" if pd.notna(ticker_data['rsi']) else "N/A")
            with col4:
                st.metric("MA50", f"₹{ticker_data['ma50']:.2f}" if ticker_data['ma50'] else "N/A")
            with col5:
                st.metric("MA200", f"₹{ticker_data['ma200']:.2f}" if ticker_data['ma200'] else "N/A")
            
            # Technical indicators interpretation
            st.subheader("📊 Technical Signals")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**RSI Interpretation**")
                rsi = ticker_data['rsi']
                if pd.notna(rsi):
                    if rsi > 70:
                        st.warning(f"⚠️ Overbought ({rsi:.0f})")
                    elif rsi < 30:
                        st.success(f"✅ Oversold ({rsi:.0f})")
                    else:
                        st.info(f"➡️ Neutral ({rsi:.0f})")
                else:
                    st.info("N/A")
            
            with col2:
                st.markdown("**Moving Average Signal**")
                price = ticker_data['current_price']
                ma50 = ticker_data['ma50']
                ma200 = ticker_data['ma200']
                
                if ma50 and ma200:
                    if price > ma50 > ma200:
                        st.success(f"✅ Uptrend (Price > MA50 > MA200)")
                    elif price < ma50 < ma200:
                        st.error(f"❌ Downtrend (Price < MA50 < MA200)")
                    else:
                        st.info(f"➡️ Transition Phase")
                else:
                    st.info("Insufficient data")
            
            with col3:
                st.markdown("**52-Week Range**")
                high_52 = ticker_data['high_52w']
                low_52 = ticker_data['low_52w']
                price = ticker_data['current_price']
                
                if high_52 and low_52:
                    range_pct = ((price - low_52) / (high_52 - low_52)) * 100
                    st.info(f"📍 {range_pct:.0f}% of 52w range")
                    st.caption(f"High: ₹{high_52:.2f} | Low: ₹{low_52:.2f}")
                else:
                    st.info("N/A")
            
            # Price history chart
            try:
                ticker_clean = selected_ticker.replace('.NS', '')
                stock = yf.Ticker(selected_ticker)
                hist = stock.history(period="90d")
                
                if not hist.empty:
                    st.subheader("📉 90-Day Price Chart")
                    
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=hist.index,
                        y=hist['Close'],
                        mode='lines',
                        name='Price',
                        line=dict(color='#1f77b4', width=2)
                    ))
                    
                    # Add moving averages
                    if len(hist) >= 50:
                        ma50_vals = hist['Close'].rolling(50).mean()
                        fig.add_trace(go.Scatter(
                            x=hist.index,
                            y=ma50_vals,
                            mode='lines',
                            name='MA50',
                            line=dict(color='orange', dash='dash')
                        ))
                    
                    if len(hist) >= 200:
                        ma200_vals = hist['Close'].rolling(200).mean()
                        fig.add_trace(go.Scatter(
                            x=hist.index,
                            y=ma200_vals,
                            mode='lines',
                            name='MA200',
                            line=dict(color='red', dash='dash')
                        ))
                    
                    fig.update_layout(
                        title=f"{selected_ticker} - 90 Day Price Chart",
                        xaxis_title="Date",
                        yaxis_title="Price (₹)",
                        height=500,
                        hovermode='x unified'
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
            except Exception:
                st.warning("Could not fetch price history")
        else:
            st.warning("❌ Could not fetch data for any tickers")

with tab4:
    st.header("📉 Performance Tracking")
    
    watchlist_df = load_watchlist()
    
    if watchlist_df.empty:
        st.info("📭 Upload watchlist first (Tab 1)")
    else:
        # Fetch data
        watchlist_data = []
        for ticker in watchlist_df['ticker']:
            data = get_stock_data(ticker)
            if data:
                watchlist_data.append(data)
        
        if watchlist_data:
            data_df = pd.DataFrame(watchlist_data)
            
            st.subheader("📊 Day Performance")
            
            # Sort by day change
            perf_df = data_df[[
                'symbol', 'current_price', 'day_change'
            ]].dropna().sort_values('day_change', ascending=False)
            
            # Gainers chart
            fig = px.bar(
                perf_df.sort_values('day_change'),
                x='day_change',
                y='symbol',
                color='day_change',
                color_continuous_scale=['red', 'yellow', 'green'],
                orientation='h',
                title="Daily Performance (% Change)",
                text='day_change'
            )
            
            fig.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
            fig.update_layout(height=max(400, len(perf_df) * 25), showlegend=False)
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Top gainers/losers
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("🚀 Top Gainers")
                gainers = perf_df.head(5)[['symbol', 'day_change']].copy()
                gainers.columns = ['Ticker', 'Change %']
                st.dataframe(
                    gainers,
                    column_config={
                        "Change %": st.column_config.NumberColumn("Change %", format="%.2f%%")
                    },
                    width='stretch',
                    hide_index=True
                )
            
            with col2:
                st.subheader("📉 Top Losers")
                losers = perf_df.tail(5)[['symbol', 'day_change']].copy()
                losers.columns = ['Ticker', 'Change %']
                st.dataframe(
                    losers,
                    column_config={
                        "Change %": st.column_config.NumberColumn("Change %", format="%.2f%%")
                    },
                    width='stretch',
                    hide_index=True
                )
        else:
            st.warning("❌ Could not fetch data for any tickers")

# Footer
st.divider()
st.caption(f"✅ Stage 02 - Watchlist & Research | {datetime.now().strftime('%H:%M:%S')}")
