FROM python:3.15.0a6-alpine3.23

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN addgroup -S observ && adduser -S observ -G observ

COPY main.py .
RUN chown -R observ:observ /app
USER observ

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]