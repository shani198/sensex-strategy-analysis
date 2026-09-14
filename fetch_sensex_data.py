import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pickle

# Fetch 3 years of Sensex data
print("Fetching Sensex data from Yahoo Finance...")
print("=" * 60)

# Download daily data for 3 years
end_date = datetime.now()
start_date = end_date - timedelta(days=3*365)

sensex = yf.download('^BSESN', start=start_date.strftime('%Y-%m-%d'), 
                     end=end_date.strftime('%Y-%m-%d'), progress=False)

print(f"\n✓ Data fetched successfully!")
print(f"Date range: {sensex.index[0].date()} to {sensex.index[-1].date()}")
print(f"Total trading days: {len(sensex)}")
print(f"\nData shape: {sensex.shape}")
print(f"\nFirst few rows:")
print(sensex.head())
print(f"\nLast few rows:")
print(sensex.tail())

# Save raw data
sensex.to_csv('sensex_raw_data.csv')
print(f"\n✓ Raw data saved to: sensex_raw_data.csv")

# Calculate basic statistics
print("\n" + "=" * 60)
print("SENSEX DATA STATISTICS (Last 3 Years)")
print("=" * 60)
print(f"Starting Price: ₹{sensex['Close'].iloc[0]:,.2f}")
print(f"Ending Price: ₹{sensex['Close'].iloc[-1]:,.2f}")
print(f"Return: {((sensex['Close'].iloc[-1] / sensex['Close'].iloc[0]) - 1) * 100:.2f}%")
print(f"\nHigh: ₹{sensex['High'].max():,.2f}")
print(f"Low: ₹{sensex['Low'].min():,.2f}")
print(f"Avg Daily Volume: {sensex['Volume'].mean():,.0f}")
print(f"Avg Daily Range: ₹{(sensex['High'] - sensex['Low']).mean():,.2f}")
print(f"Max Daily Move: ₹{(sensex['High'] - sensex['Low']).max():,.2f}")

# Add technical indicators
print("\n" + "=" * 60)
print("Calculating Technical Indicators...")
print("=" * 60)

# Moving Averages
sensex['MA_5'] = sensex['Close'].rolling(window=5).mean()
sensex['MA_10'] = sensex['Close'].rolling(window=10).mean()
sensex['MA_20'] = sensex['Close'].rolling(window=20).mean()
sensex['MA_50'] = sensex['Close'].rolling(window=50).mean()

# Bollinger Bands
sensex['BB_20_STD'] = sensex['Close'].rolling(window=20).std()
sensex['BB_20_UPPER'] = sensex['MA_20'] + (sensex['BB_20_STD'] * 2)
sensex['BB_20_LOWER'] = sensex['MA_20'] - (sensex['BB_20_STD'] * 2)

# RSI Calculation
def calculate_rsi(data, period=14):
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

sensex['RSI_14'] = calculate_rsi(sensex['Close'], 14)

# MACD
exp1 = sensex['Close'].ewm(span=12, adjust=False).mean()
exp2 = sensex['Close'].ewm(span=26, adjust=False).mean()
sensex['MACD'] = exp1 - exp2
sensex['MACD_SIGNAL'] = sensex['MACD'].ewm(span=9, adjust=False).mean()
sensex['MACD_HIST'] = sensex['MACD'] - sensex['MACD_SIGNAL']

# Daily Range and Gap
sensex['Daily_Range'] = sensex['High'] - sensex['Low']
sensex['Daily_Change'] = sensex['Close'].pct_change() * 100
sensex['Gap'] = sensex['Open'] - sensex['Close'].shift(1)

print("✓ Indicators calculated:")
print("  - Moving Averages (5, 10, 20, 50)")
print("  - Bollinger Bands (20, 2 std)")
print("  - RSI (14)")
print("  - MACD")
print("  - Daily Range & Gap")

# Save enriched data
sensex.to_csv('sensex_with_indicators.csv')
print(f"\n✓ Data with indicators saved to: sensex_with_indicators.csv")

# Save as pickle for faster loading
with open('sensex_data.pkl', 'wb') as f:
    pickle.dump(sensex, f)
print(f"✓ Data saved as pickle: sensex_data.pkl")

print("\n" + "=" * 60)
print("DATA PREPARATION COMPLETE!")
print("=" * 60)
print("\nReady for strategy backtesting...")
