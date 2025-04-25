import yfinance as yf
import pandas as pd

def fetch_history(asset: str, start_date: pd.Timestamp, initial_price: float) -> pd.DataFrame:
    ticker = yf.Ticker(asset)
    hist = ticker.history(start="2001-01-01").reset_index()
    hist = hist[['Date', 'Close']]
    hist['ticket'] = asset
    hist['Date'] = hist['Date'].dt.date
    intial_ratio = initial_price / hist.loc[hist['Date'] == start_date.date(), 'Close'].iloc[0]
    hist.loc[hist['Date']>=start_date.date(),'price'] = hist["Close"] * intial_ratio
    hist.loc[hist['Date'] == start_date.date(), 'EntryDate'] = True
    return hist

def fetch_basic_info(asset: str) -> pd.DataFrame:
    info = yf.Ticker(asset).info
    data = {
        "ticker": asset,
        "shortName": info.get("shortName", ""),
        "sector": info.get("sector", ""),
        "currency": info.get("currency", ""),
        "market": info.get("market", "")
    }
    return pd.DataFrame([data])
