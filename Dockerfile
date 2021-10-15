FROM python:3.9-slim-buster

RUN apt-get -y update
RUN apt-get -y install nginx \
    && apt-get -y install python3-dev \
    && apt-get -y install build-essential \
    && apt-get -y install libpq-dev

WORKDIR /app

COPY requirements-dash.txt ./requirements.txt

RUN pip install -r requirements.txt

COPY uwsgi.ini ./
COPY nginx.conf /etc/nginx
COPY SeismicPortal ./SeismicPortal
COPY db_helper ./db_helper
COPY start-dash-srv.sh ./
COPY assets ./assets
COPY dash_app.py ./
COPY downloads.py ./

ENV MPLCONFIGDIR="/tmp/matplotlib_config"

RUN chmod +x ./start-dash-srv.sh
CMD ["./start-dash-srv.sh"]