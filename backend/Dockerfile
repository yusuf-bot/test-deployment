FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy app files
COPY . .

# Ensure .env is copied into container
COPY .env .env

CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
