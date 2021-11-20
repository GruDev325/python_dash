FROM python:latest

ENV MARIADB_PROD_USER=qrr_read_analytics, MARIADB_PROD_PASS=Moe24S4SG49Ivj0EKcMWxYread, MARIADB_PRODDB_HOST=analytics-db.cgsdwsart7rn.sa-east-1.rds.amazonaws.com, MARIADB_PROD_DB_NAME=analytics_db

WORKDIR /qrr-dash

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY apps/PlotLiveData.py .
COPY assets ./assets

CMD [ "gunicorn", "PlotLiveData:server", "-w", "2", "--threads", "4", "-b", ":8050"]

