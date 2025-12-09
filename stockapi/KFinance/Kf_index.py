import pandas as pd
from urllib.parse import urljoin
from vnstock import Vnstock
from vnstock import Quote
from vnstock.botbuilder.noti import Messenger
from datetime import datetime,timedelta,date
import matplotlib.pyplot as plt
import os
import zipfile

root_folder = os.path.dirname(os.path.abspath(__file__))

def MFI(stock, start_date, end_date, df = None):
    if df is None:
        print("Reading stock data from file...")
        file_path = os.path.join(root_folder, 'data', 'stock_history', f'{stock}', f'{stock}_historyinfo.csv')
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Stock data file not found: {file_path}")
        
        df = pd.read_csv(file_path)
        
        # Convert 'time' column to datetime if it's not already
        df['time'] = pd.to_datetime(df['time'])
        
        # Filter data between start_date and end_date
        start = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)
        df = df[(df['time'] >= start) & (df['time'] <= end)].copy()
        
        df = df.sort_values('time').reset_index(drop=True)
        
        if len(df) == 0:
            raise ValueError(f"No data found for {stock} between {start_date} and {end_date}")
    
    df['Typical Price'] = (df['high'] + df['low'] + df['close'])/3
    df['Money Flow Type'] = ''
    
    for i in range(0, len(df)-1):
        j = i + 1
        if df.iloc[j, df.columns.get_loc('Typical Price')] >= df.iloc[i, df.columns.get_loc('Typical Price')]:
            df.iloc[j, df.columns.get_loc('Money Flow Type')] = 'P'
        if df.iloc[j, df.columns.get_loc('Typical Price')] < df.iloc[i, df.columns.get_loc('Typical Price')]:
            df.iloc[j, df.columns.get_loc('Money Flow Type')] = 'N'
    
    df = df[1:]
    df.reset_index(inplace=True, drop=True)
    
    negav = df.loc[df['Money Flow Type'] == 'N', 'Typical Price'].sum()
    Posi = df.loc[df['Money Flow Type'] == 'P', 'Typical Price'].sum()
    
    if negav == 0:
        raise ValueError(f"No negative money flow found for {stock}. Cannot calculate MFI.")
    
    money_ratio = Posi/negav
    MFI = 100 - 100/(1+money_ratio)
    
    return {'mfi': MFI, 'data' : df}

def CompanyInfo(stock):
    init = Vnstock().stock(symbol = stock, source = 'TCBS').company
    shareholders = init.shareholders()
    news = init.news()
    profile = init.profile()
    officers = init.officers()
    subsid = init.subsidiaries()
    com_data = [
        (shareholders,'shareholders.csv'),
        (news,'news.csv'),
        (profile,'profile.csv'),
        (officers,'officers.csv'),
        (subsid,'subsid.csv')
    ]
    direct = root_folder + f'\data\stock_info\\{stock}'
    if not os.path.exists(direct):
        os.mkdir(direct)

    for df,filename in com_data:
        df.to_csv(os.path.join(direct,filename), index = False)
    zipfile_name = direct + f'/{stock}_companyInfo.zip'
    with zipfile.ZipFile(zipfile_name, 'w') as zipf:
        for df, filename in com_data:
            file_path = os.path.join(direct, filename)
            zipf.write(file_path, arcname=filename)
    for df, filename in com_data:
        os.remove(os.path.join(direct, filename))
