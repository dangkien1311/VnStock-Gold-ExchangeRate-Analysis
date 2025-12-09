import time
from airflow.decorators import dag, task
from airflow.models import DagRun
from airflow.utils.session import create_session
from datetime import datetime, timedelta
import sys
import os

sys.path.insert(0, os.path.abspath('/opt/airflow'))
from stockapi.KFinance import Kf_function as Kff

stocks = ['HPG','VND','SAB','MBB','MML','FPT','TCB','MCH','VCB']
today = datetime.today().strftime('%Y-%m-%d')

default_args = {
    "owner": "Kiendt",
    "depends_on_past": False,
    "start_date": datetime(2025, 5, 20),
    "email": ["kiendt.1311@gmail.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}

@dag(
    dag_id="get_data_stock",
    description="Create stock data for prediction model",
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
    tags=["finance", "data_collection"],
)
def get_data_stock_dag():
    @task
    def fetch_stock_data(stocks, date):
        number_days = 1022
        end = datetime.strptime(date, '%Y-%m-%d').date()
        start = (end - timedelta(days=number_days)).strftime('%Y-%m-%d')
        end = end.strftime('%Y-%m-%d')
        for stock in stocks:
            Kff.get_stock_history(stock=stock, start_date=start, end_date=end)
        return f"Stock data for {stocks} from {start} to {end} fetched."
    
    @task
    def caculate_index_for_stocks(stocks):
        for stock in stocks:
            Kff.caculate_index(stock)
        return f"indexes calculated for stocks: {stocks}."
    fetch_stock_data(stocks, today) >> caculate_index_for_stocks(stocks)
get_data_stock = get_data_stock_dag()


@dag(
    dag_id="Stock_analysis",
    description="Run stock analysis index calculation and visualization",
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
    tags=["finance", "stock_analysis", "visualization"],
)
def index_analysis_dag():
    @task
    def check_missing_date():
        with create_session() as session:
            last_run = (
                session.query(DagRun)
                .filter(DagRun.dag_id == 'mfi_index')
                .filter(DagRun.state == "success")
                .order_by(DagRun.execution_date.desc())
                .first()
            )

        today = datetime.today().date()
        last_date = last_run.execution_date.date() if last_run else today 

        missing_dates = []
        check_date = last_date

        while check_date < today:
            missing_dates.append(check_date.isoformat())
            check_date += timedelta(days=1)

        print("Last run:", last_run)
        print("Missing dates:", missing_dates)
        return missing_dates
    
    @task
    def fetch_stock_data(stocks, date):
        number_days = 1022
        end = datetime.strptime(date, '%Y-%m-%d').date()
        start = (end - timedelta(days=number_days)).strftime('%Y-%m-%d')
        end = end.strftime('%Y-%m-%d')
        for stock in stocks:
            Kff.get_stock_history(stock=stock, start_date=start, end_date=end)
        return f"Stock data for {stocks} from {start} to {end} fetched."
    
    @task
    def caculate_index_for_stocks(stocks):
        for stock in stocks:
            Kff.caculate_index(stock)
        return f"indexes calculated for stocks: {stocks}."

    @task
    def visualize_index(stocks, list_date):
        today = datetime.today().strftime('%Y-%m-%d')

        if not list_date:
            print(f"Visualizing for: {today}")
            Kff.visualize_stock_indicators(stocks, today)
        else:
            for d in list_date:
                print(f"Running visualization for missing date: {d}")
                Kff.visualize_stock_indicators(stocks, d)
        return "Visualization complete."

    # Task dependencies
    missing = check_missing_date()
    fetch_stock_data(stocks, today) >> caculate_index_for_stocks(stocks) >> visualize_index(stocks, missing)

index_analysis = index_analysis_dag()

@dag(
    dag_id="VND_exchange_rate",
    description="Return exchange rate between VND and other currencies",
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
    tags=["finance", "exchange_rate"],
)
def exchange_rate_dag():

    @task
    def calculate_exchange_rate(date):
        print(f"Calculating exchange rate for: {date}")
        return Kff.exchange_rate(date)

    calculate_exchange_rate(today)

exchange_rate = exchange_rate_dag()
