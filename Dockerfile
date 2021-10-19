FROM python:3.9-slim-buster

RUN apt-get -y update
RUN apt-get -y install nginx \
    && apt-get -y install python3-dev \
    && apt-get -y install build-essential \
    && apt-get -y install libpq-dev

WORKDIR /app

COPY requirements-dash.txt ./requirements.txt

RUN pip install -r requirements.txt

COPY ./app ./app
COPY uwsgi.ini ./
COPY nginx.conf /etc/nginx
COPY start-dash-srv.sh ./
COPY run.py ./

ENV MPLCONFIGDIR="/tmp/matplotlib_config"

RUN chmod +x ./start-dash-srv.sh
CMD ["./start-dash-srv.sh"]