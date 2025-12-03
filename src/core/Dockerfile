FROM python:3.11-slim-bookworm

WORKDIR /app

COPY requirements.txt .

RUN apt update && apt install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

RUN pip install -r requirements.txt

COPY . . 
