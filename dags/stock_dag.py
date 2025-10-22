from airflow.decorators import dag, task
from airflow.models import DagRun
from airflow.utils.session import create_session
from datetime import datetime, timedelta
import sys
import os

sys.path.insert(0, os.path.abspath('/opt/airflow'))
from stockapi.KFinance import Kf_function as Kff

stocks = ['MML', 'MBB']
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
        number_days = 300
        end = datetime.strptime(date, '%Y-%m-%d').date()
        start = (end - timedelta(days=number_days)).strftime('%Y-%m-%d')
        end = end.strftime('%Y-%m-%d')
        Kff.stock_history(stock=stocks, start_date=start, end_date=end)
        return f"Stock data for {stocks} from {start} to {end} fetched."

    fetch_stock_data("TCB", today)
get_data_stock = get_data_stock_dag()


@dag(
    dag_id="mfi_index",
    description="Calculate MFI index for stocks",
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
    tags=["finance", "MFI"],
)
def mfi_index_dag():

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
        last_date = last_run.execution_date.date() if last_run else (today - timedelta(days=1))

        missing_dates = []
        check_date = last_date

        while check_date < (today - timedelta(days=1)):
            missing_dates.append(check_date.isoformat())
            check_date += timedelta(days=1)

        print("Last run:", last_run)
        print("Missing dates:", missing_dates)
        return missing_dates

    @task
    def calculate_mfi(stocks, list_date):
        today = datetime.today().strftime('%Y-%m-%d')

        if not list_date:
            print(f"Running MFI for today: {today}")
            Kff.run_mfi(stocks, today)
        else:
            for d in list_date:
                print(f"Running MFI for missing date: {d}")
                Kff.run_mfi(stocks, d)
        return "MFI calculation complete."

    # Task dependencies
    missing = check_missing_date()
    calculate_mfi(stocks, missing)

mfi_index = mfi_index_dag()

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
