import yfinance as yf
import pandas as pd
import ta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

# Lista de tickers em uma linha, aspas simples
tickers = ['PETR4.SA','PETR3.SA','VALE3.SA','ITUB4.SA','BBAS3.SA','BBDC4.SA','ABEV3.SA','MGLU3.SA','B3SA3.SA','SUZB3.SA','KLBN11.SA','GGBR4.SA','EMBR3.SA','LREN3.SA','BIDI11.SA','BOVA11.SA','IVVB11.SA','SMAL11.SA','AAPL','MSFT','AMZN','TSLA','GOOGL','META','NFLX','NVDA','INTC','KO','PEP','DIS','JNJ','JPM','BAC','SPY','QQQ','DIA','EEM','GLD','USO','BTC-USD','ETH-USD','ADA-USD','SOL-USD','DOGE-USD','DOT-USD','XRP-USD']

def fetch_data(ticker):
    df = yf.download(ticker, period='6mo', interval='1d')
    return df

def calculate_indicators(df):
    close_series = df['Close'].squeeze()
    df['rsi'] = ta.momentum.RSIIndicator(close_series).rsi().astype(float)
    df['sma50'] = close_series.rolling(50).mean().astype(float)
    df['sma200'] = close_series.rolling(200).mean().astype(float)
    return df

def send_email(signal_info):
    sender_email = os.environ.get("EMAIL_USER")
    sender_password = os.environ.get("EMAIL_PASS")
    receiver_email = os.environ.get("EMAIL_RECEIVER")

    subject = f"Sinal {signal_info['Signal']}: {signal_info['Ticker']}"
    body = f"""
Ativo: {signal_info['Ticker']}
Data: {signal_info['Date']}
Fechamento: {signal_info['Close']}
RSI: {signal_info['RSI']}
Sinal: {signal_info['Signal']}
"""

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)
        print(f"E-mail enviado: {signal_info['Ticker']}")
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")

def analyze_ticker(ticker):
    df = fetch_data(ticker)
    df = calculate_indicators(df)
    latest = df.iloc[-1]

    rsi = float(latest['rsi'].iloc[0]) if hasattr(latest['rsi'], 'iloc') else float(latest['rsi'])
    sma50 = float(latest['sma50'].iloc[0]) if hasattr(latest['sma50'], 'iloc') else float(latest['sma50'])
    sma200 = float(latest['sma200'].iloc[0]) if hasattr(latest['sma200'], 'iloc') else float(latest['sma200'])
    close = float(latest['Close'].iloc[0]) if hasattr(latest['Close'], 'iloc') else float(latest['Close'])

    # lógica do sinal
    if rsi < 30 and sma50 > sma200:
        signal = 'STRONG BUY'
    elif rsi < 50 and sma50 > sma200:
        signal = 'BUY'
    elif rsi > 70 or sma50 < sma200:
        signal = 'SELL'
    else:
        signal = 'HOLD'

    # envia e-mail apenas nos sinais fortes
    if signal in ['STRONG BUY', 'SELL']:
        send_email({
            'Ticker': ticker,
            'Date': latest.name.strftime('%Y-%m-%d'),
            'Close': close,
            'RSI': rsi,
            'Signal': signal
        })

    return {
        'Ticker': ticker,
        'Date': latest.name.strftime('%Y-%m-%d'),
        'Close': close,
        'RSI': rsi,
        'Signal': signal
    }

def main():
    results = []
    for ticker in tickers:
        results.append(analyze_ticker(ticker))
    df_res = pd.DataFrame(results)
    df_res.to_csv('signals.csv', index=False)
    print("Arquivo signals.csv gerado!")

if __name__ == "__main__":
    main()
