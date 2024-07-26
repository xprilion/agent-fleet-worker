FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt requirements.txt
COPY .env .env
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "app.py"]
