FROM python:3.12-slim

WORKDIR /app

# Install deps first for better layer caching
COPY data_ingestion_service/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY data_ingestion_service/data_ingestion_service.py .
COPY utils.py .
COPY couch_db_client.py .

CMD ["python", "data_ingestion_service.py"]