from vnstock.botbuilder.noti import Messenger
from vnstock.explorer.misc.gold_price import *
from vnstock.explorer.misc.exchange_rate import *
from datetime import datetime,timedelta,date
import json
import matplotlib.pyplot as plt
import Kf_index as KF
from telegram import Bot
import asyncio


with open('D:\DE\Python-Web-Scraping\KFinace\Key_info.json') as f:
    data = json.load(f)

def send_tele(header,path,type):
    end = datetime.today().strftime('%Y-%m-%d')
    noti = Messenger(platform='telegram', channel=data['telegram']['channel'], token_key=data['telegram']['token'])
    if type == 'stock':
        noti.send_message(message=f'{header} information in {end}', file_path= path,title=f'MFI index in {end}')
    if type == 'exchange':
        noti.send_message(message=f'{header} exchange rate information in {end} of vietcombank', file_path= path,title=f'Exchange rate in {end}')

def run_mfi(stocks, date):
    for stock in stocks:
        path = f'D:\DE\Python-Web-Scraping\KFinace\data\stocks\\{stock}.jpg'
        end = datetime.strptime(date, '%Y-%m-%d').date()
        start = (end - timedelta(days=21)).strftime('%Y-%m-%d')
        end = end.strftime('%Y-%m-%d')
        df = KF.MFI(stock,start,end)['data']
        base_list = df['time']
        for i in base_list:
            start = (i - timedelta(days=21)).strftime('%Y-%m-%d')
            end = i.strftime('%Y-%m-%d')
            MFI_value = KF.MFI(stock,start,end)['mfi']
            df.loc[df['time'] == i,'MFI'] = MFI_value
        chart = df.plot(kind = 'line',y = 'MFI', color = 'blue')
        for y in [20, 50, 80]:
            chart.axhline(y=y, color='r', linestyle='--', linewidth=1)
        for y in [70, 33]:
            chart.axhline(y=y, color='green', linestyle='--', linewidth=1)
        plt.savefig(path)
        send_tele(stock,path,'stock')

def exchange_rate(date):
    ex_path = f'D:\DE\Python-Web-Scraping\KFinace\data\exchang_rate\\exchange_rate_{date}.csv'
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
    go_path = f'D:\DE\Python-Web-Scraping\KFinace\data\gold_price\\gold_price.csv'
    df = btmc_goldprice()
    df.to_csv(go_path)
    bot = Bot(data['telegram']['token'])
    with open(go_path, "rb") as file:
        asyncio.run(bot.send_document(chat_id=data['telegram']['channel'], document=file, caption="Here is your CSV file!"))

def get_comInfo(stock):
    go_path = f'D:\DE\Python-Web-Scraping\KFinace\data\stock_info\\{stock}\\{stock}_companyInfo.zip'
    KF.CompanyInfo(stock)
    bot = Bot(data['telegram']['token'])
    with open(go_path, "rb") as file:
        asyncio.run(bot.send_document(chat_id=data['telegram']['channel'], document=file, caption=f"Here is company information of {stock}!"))