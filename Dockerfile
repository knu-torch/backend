FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN apt-get update
RUN apt-get install -y pkg-config python3-dev default-libmysqlclient-dev build-essential
RUN pip install -r requirements.txt

CMD [ "python3", "main.py" ]