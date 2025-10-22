FROM apache/airflow:2.4.2-python3.10

# Install system dependencies as root
USER root
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential && \
    rm -rf /var/lib/apt/lists/*

RUN pip uninstall -y cryptography pyOpenSSL || true

# Switch back to airflow user
USER airflow

COPY requirements.txt /
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir "apache-airflow==${AIRFLOW_VERSION}" -r /requirements.txt