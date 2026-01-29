NSE_INDICES = {
    "NIFTY 50": {
        "symbol": "^NSEI",
        "stocks": [
            "RELIANCE.NS", "TCS.NS", "HDFC.NS", "HDFCBANK.NS", "ICICIBANK.NS",
            "INFY.NS", "WIPRO.NS", "LT.NS", "ITC.NS", "AXISBANK.NS",
            "HINDUNILVR.NS", "MARUTI.NS", "SUNPHARMA.NS", "ASIANPAINT.NS",
            "HCLTECH.NS", "TECHM.NS", "BAJAJFINSV.NS", "SBIN.NS", "KOTAKBANK.NS",
            "ULTRACEMCO.NS", "NESTLEIND.NS", "POWERGRID.NS", "TITAN.NS",
            "DMART.NS", "JSWSTEEL.NS", "TATAMOTORS.NS", "M&M.NS",
            "ADANIPOWER.NS", "ADANIGREEN.NS", "HEROMOTOCO.NS", "BAJAJ-AUTO.NS",
            "BOSCHLTD.NS", "HINDPETRO.NS", "ONGC.NS", "NTPC.NS", "GAIL.NS",
            "EICHERMOT.NS", "TATASTEEL.NS", "LUPIN.NS", "DIVISLAB.NS",
            "PHARMEASY.NS", "APOLLOHOSP.NS", "LICI.NS", "SBILIFE.NS",
            "HDFCAMC.NS", "INDIGOAP.NS"
        ]
    },
    "NIFTY NEXT 50": {
        "symbol": "^NIFTY50VALUE",
        "stocks": [
            "TRENT.NS", "MNDMNYSEC.NS", "BERGEPAINT.NS", "PGINVIT.NS",
            "VIVERVOLUP.NS", "PIDILITIND.NS", "COFORGE.NS", "PUWH.NS",
            "BLUEDARTING.NS", "CHOLAFIN.NS", "GODREJCP.NS", "GODREJPROP.NS",
            "INDIGO.NS", "KPITTECH.NS", "LTIM.NS", "LUPIN.NS",
            "MAHABANK.NS", "MANAPPURAM.NS", "MAXHEALTH.NS", "MOMENTON.NS",
            "NAHARINDUS.NS", "NATIONALUM.NS", "NMDC.NS", "NURECA.NS",
            "OBEROIRLTY.NS", "PAGEIND.NS", "PARAGMICRO.NS", "PEARLPOLY.NS",
            "PENNON.NS", "PHILIPCARB.NS", "PIIND.NS", "PIDLITE.NS",
            "PRECISION.NS", "QUESS.NS", "RADICON.NS", "RBLBANK.NS",
            "RECLTD.NS", "RELINFRA.NS", "RENUKA.NS", "RESTRICON.NS",
            "SANSTECH.NS", "SCPL.NS", "SEQUENT.NS", "SHARDACROP.NS",
            "SHRIRAMCIT.NS", "SIEMENS.NS", "SKFINDIA.NS", "SOBHA.NS"
        ]
    },
    "NIFTY BANK": {
        "symbol": "^NSEBANK",
        "stocks": [
            "HDFCBANK.NS", "ICICIBANK.NS", "AXISBANK.NS", "SBIN.NS",
            "KOTAKBANK.NS", "INDUSIND.NS", "FEDERALBNK.NS", "IDBIBANK.NS",
            "RBLBANK.NS", "YESBANK.NS", "IDFCFIRSTB.NS"
        ]
    },
    "NIFTY IT": {
        "symbol": "^CNXIT",
        "stocks": [
            "TCS.NS", "INFY.NS", "WIPRO.NS", "HCLTECH.NS", "TECHM.NS",
            "LTIM.NS", "COFORGE.NS", "KPITTECH.NS", "MPHASIS.NS", "MINDTREE.NS"
        ]
    },
    "NIFTY PHARMA": {
        "symbol": "^CNXPHARMA",
        "stocks": [
            "SUNPHARMA.NS", "LUPIN.NS", "CIPLA.NS", "DIVISLAB.NS",
            "GLENMARK.NS", "IBREALESTIND.NS", "LAURUSLAB.NS", "TORNTPHARM.NS",
            "NATCPHARMA.NS", "APOLLOHOSP.NS"
        ]
    },
    "NIFTY FMCG": {
        "symbol": "^CNXFMCG",
        "stocks": [
            "HINDUNILVR.NS", "NESTLEIND.NS", "ITC.NS", "BRITANNIA.NS",
            "MARICO.NS", "GODREJCP.NS", "COLPAL.NS", "JYOTHYLAB.NS"
        ]
    },
    "NIFTY PRIVATE BANK": {
        "symbol": "^CNXPVTBANK",
        "stocks": [
            "HDFCBANK.NS", "ICICIBANK.NS", "AXISBANK.NS", "KOTAKBANK.NS",
            "INDUSIND.NS", "FEDERALBNK.NS", "IDFCFIRSTB.NS", "RBLBANK.NS"
        ]
    },
    "NIFTY PSU BANK": {
        "symbol": "^CNXPSUBANK",
        "stocks": [
            "SBIN.NS", "IDBIBANK.NS", "UNIONBANK.NS", "INDIANBANK.NS",
            "CENTRALBK.NS", "BANKINDIA.NS", "UCOBANK.NS", "CANBK.NS"
        ]
    },
    "NIFTY ENERGY": {
        "symbol": "^CNXENERGY",
        "stocks": [
            "ONGC.NS", "NTPC.NS", "GAIL.NS", "RELIANCE.NS", "POWERGRID.NS",
            "ADANIPOWER.NS", "ADANIGREEN.NS", "TATASTEEL.NS", "JSWSTEEL.NS"
        ]
    },
    "NIFTY INFRASTRUCTURE": {
        "symbol": "^CNXINFRA",
        "stocks": [
            "POWERGRID.NS", "LT.NS", "RELINFRA.NS", "HINDCONSTR.NS",
            "INDIANHRTG.NS", "IITL.NS", "NCC.NS", "NATIONALUM.NS"
        ]
    }
}

# Commodities & Forex
COMMODITIES = {
    "COMEX Gold (USD/oz)": "GC=F",
    "COMEX Silver (USD/oz)": "SI=F",
    "INR = Gold (₹/gram)": "GOLDINR=X",
    "INR = Silver (₹/kg)": "SILVERINR=X",
    "USD/INR": "INR=X",
    "CAD/INR": "CADINR=X",
    "Dollar Index": "DXY",
    "NIFTY 50": "^NSEI",
    "SENSEX": "^BSESN",
}

# Helper functions
def get_all_indices():
    """Get list of all available indices"""
    return list(NSE_INDICES.keys())

def get_stocks_for_index(index_name):
    """Get stock list for a specific index"""
    if index_name in NSE_INDICES:
        return sorted(NSE_INDICES[index_name]["stocks"])
    return []

def get_all_stocks():
    """Get all unique stocks across all indices"""
    all_stocks = set()
    for index_data in NSE_INDICES.values():
        all_stocks.update(index_data["stocks"])
    return sorted(list(all_stocks))

def get_commodity_list():
    """Get list of commodities"""
    return list(COMMODITIES.keys())

def get_commodity_ticker(commodity_name):
    """Get ticker for commodity"""
    return COMMODITIES.get(commodity_name)
