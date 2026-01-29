"""
0002_Watchlist_Stage02_Watchlist_and_Research.py

Watchlist Management & Research
- Simple CSV: filename.csv with one ticker per line
- Fetch live prices + key metrics (P/E, Dividend Yield, 52-week range)
- Technical indicators (RSI, MA50, MA200, SuperTrend 10,2 / 10,3 / 20,5)
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

# import your utils module
from utils import indicators  # assumes utils/indicators.py

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
def get_stock_data(ticker: str):
    """Fetch comprehensive stock data from yfinance + indicators utils"""
    if pd.isna(ticker) or not str(ticker).strip():
        return None

    ticker_clean = str(ticker).strip().upper()

    # If user already gave ITC.NS, use as-is; otherwise add .NS for NSE names
    nse_keywords = [
        'HDFC', 'HDFCBANK', 'RELI', 'RELIANCE', 'ITC', 'LICI', 'LUPIN',
        'NIFTY', 'GOLD', 'SILVER', 'LIQUID',
        'GHCL', 'HAPP', 'HINDU', 'PGINVIT', 'TATVA', 'JUNIORBEES',
        'TRENT', 'ICICI'
    ]

    if ticker_clean.endswith(".NS"):
        symbol = ticker_clean
    elif any(kw in ticker_clean for kw in nse_keywords):
        symbol = f"{ticker_clean}.NS"
    else:
        symbol = ticker_clean

    try:
        stock = yf.Ticker(symbol)

        # Use shared utils to compute indicators + history
        ind = indicators.calculate_all_indicators(stock)

        # 52-week range from 365d history
        year_hist = stock.history(period="365d")
        if not year_hist.empty:
            high_52w = year_hist["High"].max()
            low_52w = year_hist["Low"].min()
        else:
            high_52w = None
            low_52w = None

        hist = ind["history"]
        if hist.empty:
            return None

        current_price = hist["Close"].iloc[-1]

        info = stock.info

        return {
            "symbol": symbol,
            "current_price": current_price,
            "ma50": ind["ma50"],
            "ma200": ind["ma200"],
            "rsi": ind["rsi"],
            "high_52w": high_52w,
            "low_52w": low_52w,
            "supertrend_102": ind["supertrend_102"],
            "supertrend_103": ind["supertrend_103"],
            "supertrend_205": ind["supertrend_205"],
            "pe_ratio": info.get("trailingPE"),
            "dividend_yield": info.get("dividendYield"),
            "market_cap": info.get("marketCap"),
            "previous_close": info.get("previousClose"),
            "day_change": (
                (current_price - info.get("previousClose", current_price))
                / info.get("previousClose", current_price)
                * 100
                if info.get("previousClose")
                else None
            ),
        }
    except Exception:
        return None


def parse_watchlist_csv(uploaded_file):
    """Parse watchlist CSV (simple: one ticker per line, with or without .NS)"""
    try:
        df = pd.read_csv(uploaded_file, header=None, names=["ticker"])
        df["ticker"] = df["ticker"].astype(str).str.strip().str.upper()
        df = df[df["ticker"].str.len() > 0].reset_index(drop=True)
        return df
    except Exception as e:
        st.error(f"❌ CSV parsing error: {str(e)}")
        st.error("Expected format: One ticker per line (e.g., ITC or ITC.NS)")
        return pd.DataFrame()


def save_watchlist(watchlist_df):
    """Save watchlist to JSON"""
    watchlist_data = watchlist_df["ticker"].tolist()
    with open(WATCHLIST_FILE, "w") as f:
        json.dump(watchlist_data, f, indent=2)
    return len(watchlist_data)


def load_watchlist():
    """Load watchlist from JSON"""
    if os.path.exists(WATCHLIST_FILE):
        try:
            with open(WATCHLIST_FILE, "r") as f:
                data = json.load(f)
            return pd.DataFrame({"ticker": data})
        except Exception:
            return pd.DataFrame()
    return pd.DataFrame()


# ============================================================================
# MAIN UI
# ============================================================================

tab1, tab2, tab3, tab4 = st.tabs(
    ["📁 Upload CSV", "📊 Watchlist View", "📈 Technical Analysis", "📉 Performance"]
)

# ---------------------------- TAB 1: UPLOAD ---------------------------------
with tab1:
    st.header("📁 Upload Watchlist CSV")

    uploaded_file = st.file_uploader(
        "Choose CSV file",
        type=["csv"],
        help="Simple format: one ticker per line (e.g., RELIANCE, HDFC, ITC, or ITC.NS)",
    )

    if uploaded_file is not None:
        watchlist_df = parse_watchlist_csv(uploaded_file)

        if not watchlist_df.empty:
            st.success(f"✅ Parsed {len(watchlist_df)} tickers")

            st.subheader("📋 Preview")
            st.dataframe(
                watchlist_df,
                width="stretch",
                hide_index=True,
            )

            if st.button("💾 Save Watchlist", type="primary", use_container_width=True):
                count = save_watchlist(watchlist_df)
                st.success(f"✅ Saved {count} tickers!")
                st.balloons()
        else:
            st.error("❌ No valid tickers found in CSV")

# -------------------------- TAB 2: WATCHLIST VIEW ---------------------------
with tab2:
    st.header("📊 Watchlist View (Live Prices)")

    watchlist_df = load_watchlist()

    if watchlist_df.empty:
        st.info("📭 **Upload CSV first** (Tab 1)")
    else:
        st.success(f"📊 {len(watchlist_df)} tickers loaded")

        st.info("🔄 Fetching live data...")
        progress_bar = st.progress(0)

        watchlist_data = []
        for i, ticker in enumerate(watchlist_df["ticker"]):
            data = get_stock_data(ticker)
            if data:
                watchlist_data.append(data)
            progress_bar.progress(min((i + 1) / len(watchlist_df), 1.0))

        if watchlist_data:
            data_df = pd.DataFrame(watchlist_data)
            successful = len(data_df)
            progress_bar.progress(100)
            st.success(f"✅ Fetched data for {successful}/{len(watchlist_df)} tickers")

            st.subheader("📋 Live Prices & Metrics")

            display_df = data_df[
                [
                    "symbol",
                    "current_price",
                    "day_change",
                    "pe_ratio",
                    "dividend_yield",
                    "rsi",
                ]
            ].copy()

            display_df.columns = [
                "Symbol",
                "Price",
                "Day Change %",
                "P/E",
                "Div Yield %",
                "RSI",
            ]

            st.dataframe(
                display_df,
                column_config={
                    "Price": st.column_config.NumberColumn("Price", format="₹%.2f"),
                    "Day Change %": st.column_config.NumberColumn(
                        "Change %", format="%.2f%%"
                    ),
                    "P/E": st.column_config.NumberColumn("P/E", format="%.2f"),
                    "Div Yield %": st.column_config.NumberColumn(
                        "Yield %", format="%.2f%%"
                    ),
                    "RSI": st.column_config.NumberColumn("RSI", format="%.0f"),
                },
                width="stretch",
                hide_index=True,
            )

            st.subheader("📈 Watchlist Summary")
            col1, col2, col3, col4 = st.columns(4)

            avg_pe = data_df["pe_ratio"].mean()
            avg_yield = data_df["dividend_yield"].mean()
            count_positive = (data_df["day_change"] > 0).sum()

            with col1:
                st.metric("Total Tickers", len(data_df))
            with col2:
                st.metric(
                    "Avg P/E", f"{avg_pe:.2f}" if pd.notna(avg_pe) else "N/A"
                )
            with col3:
                st.metric(
                    "Avg Div Yield",
                    f"{avg_yield*100:.2f}%"
                    if pd.notna(avg_yield)
                    else "N/A",
                )
            with col4:
                st.metric("Up Today", f"{count_positive}/{len(data_df)}")
        else:
            st.warning("❌ Could not fetch data for any tickers")

# ------------------------ TAB 3: TECHNICAL ANALYSIS -------------------------
with tab3:
    st.header("📈 Technical Analysis")

    watchlist_df = load_watchlist()

    if watchlist_df.empty:
        st.info("📭 Upload watchlist first (Tab 1)")
    else:
        # Re-fetch to get full history for charting
        watchlist_data = []
        for ticker in watchlist_df["ticker"]:
            data = get_stock_data(ticker)
            if data:
                watchlist_data.append(data)

        if watchlist_data:
            data_df = pd.DataFrame(watchlist_data)

            selected_ticker = st.selectbox(
                "Select ticker for detailed analysis",
                data_df["symbol"].tolist(),
            )

            ticker_row = data_df[data_df["symbol"] == selected_ticker].iloc[0]

            st.subheader(f"🔍 {selected_ticker} - Detailed Analysis")

            col1, col2, col3, col4, col5 = st.columns(5)

            with col1:
                st.metric("Price", f"₹{ticker_row['current_price']:.2f}")
            with col2:
                st.metric(
                    "P/E Ratio",
                    f"{ticker_row['pe_ratio']:.2f}"
                    if pd.notna(ticker_row["pe_ratio"])
                    else "N/A",
                )
            with col3:
                st.metric(
                    "RSI (14)",
                    f"{ticker_row['rsi']:.0f}"
                    if pd.notna(ticker_row["rsi"])
                    else "N/A",
                )
            with col4:
                st.metric(
                    "MA50",
                    f"₹{ticker_row['ma50']:.2f}"
                    if ticker_row["ma50"]
                    else "N/A",
                )
            with col5:
                st.metric(
                    "MA200",
                    f"₹{ticker_row['ma200']:.2f}"
                    if ticker_row["ma200"]
                    else "N/A",
                )

            st.subheader("📊 Technical Signals")

            col1, col2, col3 = st.columns(3)

            # RSI signal using utils
            with col1:
                st.markdown("**RSI Interpretation**")
                rsi_text, rsi_type = indicators.get_rsi_signal(
                    ticker_row["rsi"]
                )
                if rsi_type == "warning":
                    st.warning(rsi_text)
                elif rsi_type == "success":
                    st.success(rsi_text)
                else:
                    st.info(rsi_text)

            # MA signal using utils
            with col2:
                st.markdown("**Moving Average Signal**")
                ma_text, ma_type = indicators.get_ma_signal(
                    ticker_row["current_price"],
                    ticker_row["ma50"],
                    ticker_row["ma200"],
                )
                if ma_type == "success":
                    st.success(ma_text)
                elif ma_type == "error":
                    st.error(ma_text)
                else:
                    st.info(ma_text)

            # 52-week range using utils
            with col3:
                st.markdown("**52-Week Range**")
                rng_pct = indicators.get_52week_range_pct(
                    ticker_row["current_price"],
                    ticker_row["high_52w"],
                    ticker_row["low_52w"],
                )
                if rng_pct is not None:
                    st.info(f"📍 {rng_pct:.0f}% of 52w range")
                    st.caption(
                        f"High: ₹{ticker_row['high_52w']:.2f} | Low: ₹{ticker_row['low_52w']:.2f}"
                    )
                else:
                    st.info("N/A")

            # Price + SuperTrend + RSI chart
            try:
                stock = yf.Ticker(selected_ticker)
                ind_full = indicators.calculate_all_indicators(stock)
                hist = ind_full["history"]

                if not hist.empty:
                    st.subheader("📉 90-Day Price + SuperTrend + RSI")

                    hist_90 = hist.tail(90).copy()
                    st_102 = (
                        pd.Series(ind_full["st_102_full"], index=hist.index)
                        .tail(90)
                    )
                    st_103 = (
                        pd.Series(ind_full["st_103_full"], index=hist.index)
                        .tail(90)
                    )
                    st_205 = (
                        pd.Series(ind_full["st_205_full"], index=hist.index)
                        .tail(90)
                    )

                    # Recompute RSI over 90d for line subplot
                    rsi_90 = pd.Series(
                        indicators.calculate_rsi(hist["Close"], 14),
                        index=[hist.index[-1]],
                    )

                    fig = make_price_rsi_supertrend_figure(
                        hist_90, st_102, st_103, st_205
                    )

                    st.plotly_chart(fig, use_container_width=True)

            except Exception:
                st.warning("Could not fetch price history")

        else:
            st.warning("❌ Could not fetch data for any tickers")

# ------------------------- TAB 4: PERFORMANCE -------------------------------
with tab4:
    st.header("📉 Performance Tracking")

    watchlist_df = load_watchlist()

    if watchlist_df.empty:
        st.info("📭 Upload watchlist first (Tab 1)")
    else:
        watchlist_data = []
        for ticker in watchlist_df["ticker"]:
            data = get_stock_data(ticker)
            if data:
                watchlist_data.append(data)

        if watchlist_data:
            data_df = pd.DataFrame(watchlist_data)

            st.subheader("📊 Day Performance")

            perf_df = (
                data_df[["symbol", "current_price", "day_change"]]
                .dropna()
                .sort_values("day_change", ascending=False)
            )

            fig = px.bar(
                perf_df.sort_values("day_change"),
                x="day_change",
                y="symbol",
                color="day_change",
                color_continuous_scale=["red", "yellow", "green"],
                orientation="h",
                title="Daily Performance (% Change)",
                text="day_change",
            )

            fig.update_traces(
                texttemplate="%{text:.2f}%", textposition="outside"
            )
            fig.update_layout(
                height=max(400, len(perf_df) * 25),
                showlegend=False,
            )

            st.plotly_chart(fig, use_container_width=True)

            col1, col2 = st.columns(2)

            with col1:
                st.subheader("🚀 Top Gainers")
                gainers = perf_df.head(5)[["symbol", "day_change"]].copy()
                gainers.columns = ["Ticker", "Change %"]
                st.dataframe(
                    gainers,
                    column_config={
                        "Change %": st.column_config.NumberColumn(
                            "Change %", format="%.2f%%"
                        )
                    },
                    width="stretch",
                    hide_index=True,
                )

            with col2:
                st.subheader("📉 Top Losers")
                losers = perf_df.tail(5)[["symbol", "day_change"]].copy()
                losers.columns = ["Ticker", "Change %"]
                st.dataframe(
                    losers,
                    column_config={
                        "Change %": st.column_config.NumberColumn(
                            "Change %", format="%.2f%%"
                        )
                    },
                    width="stretch",
                    hide_index=True,
                )
        else:
            st.warning("❌ Could not fetch data for any tickers")

# ---------------------------------------------------------------------------
# Helper to build price + ST + RSI figure (bottom RSI panel)
# ---------------------------------------------------------------------------
from plotly.subplots import make_subplots


def make_price_rsi_supertrend_figure(hist_90, st_102, st_103, st_205):
    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_width=[0.2, 0.8],  # [RSI height, Price height]
    )

    # Price
    fig.add_trace(
        go.Scatter(
            x=hist_90.index,
            y=hist_90["Close"],
            mode="lines",
            name="Price",
            line=dict(color="#1f77b4", width=2),
        ),
        row=1,
        col=1,
    )

    # SuperTrend lines
    if st_102 is not None:
        fig.add_trace(
            go.Scatter(
                x=hist_90.index,
                y=st_102.tail(len(hist_90)),
                mode="lines",
                name="ST 10,2",
                line=dict(color="green", width=1),
            ),
            row=1,
            col=1,
        )

    if st_103 is not None:
        fig.add_trace(
            go.Scatter(
                x=hist_90.index,
                y=st_103.tail(len(hist_90)),
                mode="lines",
                name="ST 10,3",
                line=dict(color="orange", width=1),
            ),
            row=1,
            col=1,
        )

    if st_205 is not None:
        fig.add_trace(
            go.Scatter(
                x=hist_90.index,
                y=st_205.tail(len(hist_90)),
                mode="lines",
                name="ST 20,5",
                line=dict(color="red", width=1),
            ),
            row=1,
            col=1,
        )

    # RSI (recompute over 90d)
    rsi_series = hist_90["Close"].diff()  # placeholder to get index
    rsi_vals = hist_90["Close"].rolling(14).apply(
        lambda _: indicators.calculate_rsi(hist_90["Close"], 14)
    )
    fig.add_trace(
        go.Scatter(
            x=hist_90.index,
            y=rsi_vals,
            mode="lines",
            name="RSI 14",
            line=dict(color="#9467bd", width=2),
        ),
        row=2,
        col=1,
    )

    # Overbought/Oversold zones
    fig.add_hline(y=70, line=dict(color="red", dash="dash"), row=2, col=1)
    fig.add_hline(y=30, line=dict(color="green", dash="dash"), row=2, col=1)

    fig.update_yaxes(title_text="Price (₹)", row=1, col=1)
    fig.update_yaxes(title_text="RSI", row=2, col=1, range=[0, 100])

    fig.update_layout(
        height=600,
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )

    return fig


# Footer
st.divider()
st.caption(
    f"✅ Stage 02 - Watchlist & Research (utils.indicators) | {datetime.now().strftime('%H:%M:%S')}"
)
