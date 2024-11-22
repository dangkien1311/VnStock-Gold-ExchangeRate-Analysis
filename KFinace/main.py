import Kf_function as Kff
from datetime import datetime,timedelta,date

date = datetime.today().strftime('%Y-%m-%d')
# stocks = ['MML','VIC','TCB']
# Kff.run_mfi(stocks,date)
# Kff.exchange_rate(date)
Kff.gold_price()