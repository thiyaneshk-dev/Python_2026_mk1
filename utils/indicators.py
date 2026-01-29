"""
utils/indicators.py

Technical Indicator Calculations
- Moving Averages (MA50, MA200)
- SuperTrend (10,2), (10,3), (20,5)
- RSI (14-period)
- All reusable across portfolio, watchlist, and research modules
"""

import pandas as pd
import numpy as np


def calculate_ma(data, period):
    """Calculate Simple Moving Average
    
    Args:
        data: Series of close prices
        period: MA period (50, 200, etc.)
    
    Returns:
        float: Current MA value, or None if insufficient data
    """
    if len(data) < period:
        return None
    return data.tail(period).mean()


def calculate_rsi(data, period=14):
    """Calculate Relative Strength Index (RSI)
    
    Args:
        data: Series of close prices
        period: RSI period (default 14)
    
    Returns:
        float: Current RSI value (0-100), or None if insufficient data
    """
    if len(data) < period:
        return None
    
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    
    # Avoid division by zero
    rs = gain / loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    
    return rsi.iloc[-1]


def calculate_supertrend(ohlc_data, period=10, multiplier=2):
    """Calculate SuperTrend indicator
    
    Args:
        ohlc_data: DataFrame with High, Low, Close columns
        period: ATR period (default 10)
        multiplier: ATR multiplier (default 2)
    
    Returns:
        list: SuperTrend values, or None if insufficient data
    """
    if len(ohlc_data) < period:
        return None
    
    high = ohlc_data['High']
    low = ohlc_data['Low']
    close = ohlc_data['Close']
    
    # Calculate ATR (Average True Range)
    hl_avg = (high + low) / 2
    tr = high - low
    atr = tr.rolling(period).mean()
    
    # Calculate SuperTrend bands
    basic_ub = hl_avg + multiplier * atr
    basic_lb = hl_avg - multiplier * atr
    
    # Final bands with smoothing
    final_ub = [None] * len(ohlc_data)
    final_lb = [None] * len(ohlc_data)
    
    for i in range(len(ohlc_data)):
        if i == 0:
            final_ub[i] = basic_ub.iloc[i]
            final_lb[i] = basic_lb.iloc[i]
        else:
            final_ub[i] = (basic_ub.iloc[i] if basic_ub.iloc[i] < final_ub[i-1] or close.iloc[i-1] > final_ub[i-1] 
                          else final_ub[i-1])
            final_lb[i] = (basic_lb.iloc[i] if basic_lb.iloc[i] > final_lb[i-1] or close.iloc[i-1] < final_lb[i-1] 
                          else final_lb[i-1])
    
    # Determine SuperTrend (upper or lower band)
    supertrend = [None] * len(ohlc_data)
    for i in range(len(ohlc_data)):
        if i == 0:
            supertrend[i] = final_ub[i]
        else:
            supertrend[i] = (final_ub[i] if (supertrend[i-1] == final_ub[i-1] and close.iloc[i] <= final_ub[i]) 
                            else final_lb[i])
    
    return supertrend


def calculate_all_indicators(ticker_data):
    """Calculate all technical indicators at once
    
    Args:
        ticker_data: yfinance Ticker object
    
    Returns:
        dict: Dictionary with all indicators
    """
    hist = ticker_data.history(period="200d")
    
    if hist.empty or len(hist) < 14:
        return {
            'ma50': None,
            'ma200': None,
            'rsi': None,
            'supertrend_102': None,
            'supertrend_103': None,
            'supertrend_205': None,
        }
    
    ma50 = calculate_ma(hist['Close'], 50)
    ma200 = calculate_ma(hist['Close'], 200)
    rsi = calculate_rsi(hist['Close'], 14)
    
    st_102 = calculate_supertrend(hist, period=10, multiplier=2)
    st_103 = calculate_supertrend(hist, period=10, multiplier=3)
    st_205 = calculate_supertrend(hist, period=20, multiplier=5)
    
    return {
        'ma50': ma50,
        'ma200': ma200,
        'rsi': rsi,
        'supertrend_102': st_102[-1] if st_102 else None,
        'supertrend_103': st_103[-1] if st_103 else None,
        'supertrend_205': st_205[-1] if st_205 else None,
        'history': hist,  # Return full history for charting
        'st_102_full': st_102,  # Return full arrays for charts
        'st_103_full': st_103,
        'st_205_full': st_205,
    }


def get_rsi_signal(rsi_value):
    """Get RSI interpretation signal
    
    Args:
        rsi_value: RSI value (0-100)
    
    Returns:
        tuple: (signal_text, signal_type) - signal_type is 'warning', 'success', or 'info'
    """
    if rsi_value is None:
        return "N/A", "info"
    
    if rsi_value > 70:
        return f"⚠️ Overbought ({rsi_value:.0f})", "warning"
    elif rsi_value < 30:
        return f"✅ Oversold ({rsi_value:.0f})", "success"
    else:
        return f"➡️ Neutral ({rsi_value:.0f})", "info"


def get_ma_signal(price, ma50, ma200):
    """Get Moving Average trend signal
    
    Args:
        price: Current price
        ma50: 50-day MA
        ma200: 200-day MA
    
    Returns:
        tuple: (signal_text, signal_type) - signal_type is 'success', 'error', or 'info'
    """
    if ma50 is None or ma200 is None:
        return "Insufficient data", "info"
    
    if price > ma50 > ma200:
        return f"✅ Uptrend (Price > MA50 > MA200)", "success"
    elif price < ma50 < ma200:
        return f"❌ Downtrend (Price < MA50 < MA200)", "error"
    else:
        return f"➡️ Transition Phase", "info"


def get_52week_range_pct(price, high_52w, low_52w):
    """Get 52-week range percentage
    
    Args:
        price: Current price
        high_52w: 52-week high
        low_52w: 52-week low
    
    Returns:
        float: Percentage (0-100), or None if data unavailable
    """
    if high_52w is None or low_52w is None:
        return None
    
    if high_52w == low_52w:
        return None
    
    return ((price - low_52w) / (high_52w - low_52w)) * 100
