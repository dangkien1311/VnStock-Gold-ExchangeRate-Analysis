import pandas as pd
from urllib.parse import urljoin
from vnstock3 import Vnstock
from vnstock3.botbuilder.noti import Messenger
from datetime import datetime,timedelta,date
import matplotlib.pyplot as plt

def MFI(stock, start_date, end_date):
    stock = Vnstock().stock(symbol = stock, source = 'VCI')
    df = stock.quote.history(
                            start = start_date, 
                            end = end_date,
                            interval= '1D' 
                            )
    df['Typical Price'] = (df['high'] + df['low'] + df['close'])/3
    df['Money Flow Type'] = ''
    for i in range(0, len(df)-1):
        j = i + 1
        if df.iloc[j, df.columns.get_loc('Typical Price')] >= df.iloc[i, df.columns.get_loc('Typical Price')]:
            df.iloc[j, df.columns.get_loc('Money Flow Type')] = 'P'
        if df.iloc[j, df.columns.get_loc('Typical Price')] < df.iloc[i, df.columns.get_loc('Typical Price')]:
            df.iloc[j, df.columns.get_loc('Money Flow Type')] = 'N'
    df = df[1:]
    df.reset_index(inplace=True)
    negav = df.loc[df['Money Flow Type'] == 'N', 'Typical Price'].sum()
    Posi = df.loc[df['Money Flow Type'] == 'P', 'Typical Price'].sum()
    money_ratio = Posi/negav
    MFI = 100 - 100/(1+money_ratio)
    return {'mfi': MFI, 'data' : df}