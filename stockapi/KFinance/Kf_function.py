import pandas as pd
from vnstock.botbuilder.noti import Messenger
from vnstock.explorer.misc.gold_price import *
from vnstock.explorer.misc.exchange_rate import *
from datetime import datetime,timedelta,date
from vnstock import Quote
import json
import matplotlib.pyplot as plt
from stockapi.KFinance import Kf_index as KF
from telegram import Bot
import asyncio
import os
import time
import ta

root_folder = os.path.dirname(os.path.abspath(__file__))
keyJson_path = os.path.join(root_folder,"Key_info.json")

with open(keyJson_path) as f:
    data = json.load(f)

def send_tele(header,path,date,type):
    noti = Messenger(platform='telegram', channel=data['telegram']['channel'], token_key=data['telegram']['token'])
    if type == 'stock':
        noti.send_message(message=f'{header} information in {date}', file_path= path,title=f'MFI index in {date}')
    if type == 'exchange':
        noti.send_message(message=f'{header} exchange rate information in {date} of vietcombank', file_path= path,title=f'Exchange rate in {date}')

def visualize_stock_indicators(stocks, date, days_back=30):
    for stock in stocks:
        try:
            # Read data from stock_analysis_data folder
            analysis_path = os.path.join(root_folder, "data", "stock_analysis_data", stock, f"{stock}_analysis_data.csv")
            
            if not os.path.exists(analysis_path):
                print(f"No analysis data found for {stock}. Please run caculate_index first.")
                continue
            
            # Load data
            df = pd.read_csv(analysis_path)
            df['time'] = pd.to_datetime(df['time'])
            
            # Filter data up to the specified date and last N days
            end_date = pd.to_datetime(date)
            start_date = end_date - timedelta(days=days_back)
            df_filtered = df[(df['time'] >= start_date) & (df['time'] <= end_date)].copy()
            
            if len(df_filtered) == 0:
                print(f"No data available for {stock} between {start_date.date()} and {end_date.date()}")
                continue
            
            # Create figure with subplots
            fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(14, 10), sharex=True)
            fig.suptitle(f'{stock} - Technical Analysis ({date})', fontsize=16, fontweight='bold')
            
            # Plot 1: Close Price
            ax1.plot(df_filtered['time'], df_filtered['close'], color='blue', linewidth=2, label='Close Price')
            ax1.set_ylabel('Price (VND)', fontsize=12, fontweight='bold')
            ax1.set_title('Close Price', fontsize=12)
            ax1.grid(True, alpha=0.3)
            ax1.legend(loc='upper left')
            
            # Plot 2: MFI (Money Flow Index)
            ax2.plot(df_filtered['time'], df_filtered['MFI'], color='green', linewidth=2, label='MFI')
            ax2.axhline(y=80, color='red', linestyle='--', linewidth=1.5, label='Overbought (80)')
            ax2.axhline(y=50, color='gray', linestyle='--', linewidth=1, alpha=0.5, label='Neutral (50)')
            ax2.axhline(y=20, color='green', linestyle='--', linewidth=1.5, label='Oversold (20)')
            ax2.fill_between(df_filtered['time'], 80, 100, alpha=0.2, color='red')
            ax2.fill_between(df_filtered['time'], 0, 20, alpha=0.2, color='green')
            ax2.set_ylabel('MFI', fontsize=12, fontweight='bold')
            ax2.set_title('Money Flow Index (MFI)', fontsize=12)
            ax2.set_ylim(0, 100)
            ax2.grid(True, alpha=0.3)
            ax2.legend(loc='upper left', fontsize=9)
            
            # Plot 3: RSI (Relative Strength Index)
            ax3.plot(df_filtered['time'], df_filtered['RSI'], color='purple', linewidth=2, label='RSI')
            ax3.axhline(y=70, color='red', linestyle='--', linewidth=1.5, label='Overbought (70)')
            ax3.axhline(y=50, color='gray', linestyle='--', linewidth=1, alpha=0.5, label='Neutral (50)')
            ax3.axhline(y=30, color='green', linestyle='--', linewidth=1.5, label='Oversold (30)')
            ax3.fill_between(df_filtered['time'], 70, 100, alpha=0.2, color='red')
            ax3.fill_between(df_filtered['time'], 0, 30, alpha=0.2, color='green')
            ax3.set_ylabel('RSI', fontsize=12, fontweight='bold')
            ax3.set_xlabel('Date', fontsize=12, fontweight='bold')
            ax3.set_title('Relative Strength Index (RSI)', fontsize=12)
            ax3.set_ylim(0, 100)
            ax3.grid(True, alpha=0.3)
            ax3.legend(loc='upper left', fontsize=9)
            
            # Format x-axis
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            # Save chart
            stock_path = os.path.join(root_folder, "data", "stocks")
            if not os.path.exists(stock_path):
                os.makedirs(stock_path)
            chart_path = os.path.join(stock_path, f'{stock}.jpg')
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            # Get latest values for summary
            latest = df_filtered.iloc[-1]
            summary_msg = (f"{stock} Summary ({date}):\n"
                          f"Close: {latest['close']:.2f} VND\n"
                          f"MFI: {latest['MFI']:.2f}\n"
                          f"RSI: {latest['RSI']:.2f}")
            print(summary_msg)
            
            # Send to Telegram
            send_tele(stock, chart_path, date, 'stock')
            time.sleep(2)
            
        except Exception as e:
            print(f"Error processing {stock}: {str(e)}")
            continue

# Keep old function name for backward compatibility
def run_mfi(stocks, date):
    """Backward compatibility wrapper - now uses visualization function"""
    visualize_stock_indicators(stocks, date, days_back=30)

def exchange_rate(date):
    path = os.path.join(root_folder,"data","exchange_rate")
    ex_path = path + f'/exchange_rate_{date}.csv'
    df = vcb_exchange_rate(date=date)
    df['buy _cash'] = df['buy _cash'].replace('-', '0').str.replace(',', '').astype(float)
    df = df[df['buy _cash'] != 0]
    df['sell'] = df['sell'].str.replace(',', '').astype(float)
    df['exchange_rate'] = (df['buy _cash'] + df['sell'])/2
    df.to_csv(ex_path)
    bot = Bot(data['telegram']['token'])
    with open(ex_path, "rb") as file:
        asyncio.run(bot.send_document(chat_id=data['telegram']['channel'], document=file, caption="Here is your CSV file!"))

def gold_price():
    path = os.path.join(root_folder,"data","gold_price")
    go_path = path + f'/gold_price.csv'
    df = btmc_goldprice()
    df.to_csv(go_path)
    bot = Bot(data['telegram']['token'])
    with open(go_path, "rb") as file:
        asyncio.run(bot.send_document(chat_id=data['telegram']['channel'], document=file, caption="Here is your CSV file!"))

def get_comInfo(stock):
    path = os.path.join(root_folder,"data","stock_info")
    go_path = path + f'/{stock}/{stock}_companyInfo.zip'
    KF.CompanyInfo(stock)
    bot = Bot(data['telegram']['token'])
    with open(go_path, "rb") as file:
        asyncio.run(bot.send_document(chat_id=data['telegram']['channel'], document=file, caption=f"Here is company information of {stock}!"))

def get_stock_history(stock, start_date, end_date):
    quote = Quote(symbol=stock, source='VCI')
    df = quote.history(
        start=start_date, 
        end=end_date, 
        interval='1D'
        )
    direct = root_folder + f'/data/stock_history/{stock}'
    if not os.path.exists(direct):
        os.mkdir(direct)
    path = os.path.join(root_folder,"data","stock_history")
    go_path = path + f'/{stock}/{stock}_historyinfo.csv'
    df.to_csv(go_path,index=False)

def caculate_index(stock):
    direct = root_folder + f'/data/stock_history/{stock}'
    if not os.path.exists(direct):
        return "No history data found."
    df = pd.read_csv(direct + f'/{stock}_historyinfo.csv')
    window_size = 14
    df['MFI'] = ta.volume.money_flow_index(high=df['high'], low=df['low'], close=df['close'], volume=df['volume'], window=window_size)
    df['RSI'] = ta.momentum.rsi(close=df['close'], window=window_size)
    final_path = os.path.join(root_folder,"data","stock_analysis_data") + f'/{stock}'
    if not os.path.exists(final_path):
        os.mkdir(final_path)
    final_path = final_path + f'/{stock}_analysis_data.csv'
    df = df.iloc[window_size:]
    df.to_csv(final_path, index=False)