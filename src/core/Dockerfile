FROM python:3.11-bookworm

WORKDIR /app

COPY requirements.txt .

RUN apt update

RUN apt install -y libgl1-mesa-glx

RUN pip install -r requirements.txt

COPY . . 
