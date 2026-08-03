import yfinance as yf
import pandas as pd
import numpy as np
import requests
import os
import time
from datetime import datetime

BOT_TOKEN = os.environ.get('BOT_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

def send_telegram_alert(name, signal_type, price, time_str):
    if "BEARISH" in signal_type:
        emoji, action = "🔴", "SELL/SHORT"
    else:
        emoji, action = "🟢", "BUY/LONG"
    message = f"🚨 {emoji} {signal_type}\n📊 {name}\n💰 Price: {price}\n🕐 Time: {time_str}"
    try:
        requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={message}")
    except:
        pass

TICKERS = ["^NSEI", "^NSEBANK"]

def check_divergence(symbol):
    try:
        stock = yf.Ticker(symbol)
        data = stock.history(period="1d", interval="5m")
        if data.empty or len(data) < 10:
            return None, None
        data['delta'] = np.where(data['Close'] > data['Open'], data['Volume'] * 0.6, -data['Volume'] * 0.6)
        data['CVD'] = data['delta'].cumsum()
        recent = data.iloc[-10:]
        current = data.iloc[-1]
        curr_price = current['Close']
        curr_cvd = current['CVD']
        prev_high_idx = recent['Close'].idxmax()
        prev_low_idx = recent['Close'].idxmin()
        if curr_price > recent['Close'].max() and curr_cvd < recent.loc[prev_high_idx]['CVD']:
            return "🔴 BEARISH", curr_price
        elif curr_price < recent['Close'].min() and curr_cvd > recent.loc[prev_low_idx]['CVD']:
            return "🟢 BULLISH", curr_price
        return None, None
    except:
        return None, None

print("✅ Bot Started. Scanning NIFTY & BANKNIFTY only...")
while True:
    start = time.time()
    for symbol in TICKERS:
        signal, price = check_divergence(symbol)
        if signal:
            name = "NIFTY 50" if symbol == "^NSEI" else "BANK NIFTY"
            send_telegram_alert(name, signal, price, datetime.now().strftime('%H:%M'))
            time.sleep(1)
        time.sleep(0.3)
    print(f"✅ Scanned in {time.time()-start:.1f}s. Waiting 5 min...")
    time.sleep(300)
