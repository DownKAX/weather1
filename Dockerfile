FROM python:3.13-slim

WORKDIR .

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 80

COPY . .
CMD ["python", "-m", "app.main"]