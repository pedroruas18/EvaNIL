FROM python:3.7.9-slim
RUN apt-get update && apt-get upgrade

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
