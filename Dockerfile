FROM python:3.13-slim

WORKDIR /myapp

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 80
COPY . .
ENV PYTHONPATH=/myapp
RUN chmod +x start.sh
CMD ["./start.sh"]