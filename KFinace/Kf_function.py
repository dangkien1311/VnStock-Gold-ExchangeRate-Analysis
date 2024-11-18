from vnstock3.botbuilder.noti import Messenger
from datetime import datetime,timedelta,date
import json


with open('/home/kiendt/code/ETL/KFinace/Key_info.json') as f:
    data = json.load(f)

# stock = "MML"
# path = f'/home/kiendt/code/ETL/data/{stock}.jpg'
def send_tele(stock, path):
    start = (datetime.today() - timedelta(days=21)).strftime('%Y-%m-%d')
    end = datetime.today().strftime('%Y-%m-%d')
    noti = Messenger(platform='telegram', channel=data['telegram']['channel'], token_key=data['telegram']['token'])
    noti.send_message(message=f'{stock} information in {end}', file_path= path,title=f'MFI index in {end}')