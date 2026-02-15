FROM python:3.14.2-slim

WORKDIR /myapp

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && pip uninstall -y redis \
    && pip install --no-cache-dir redis

COPY . .
ENV PYTHONPATH=/myapp