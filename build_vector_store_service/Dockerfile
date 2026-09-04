FROM python:3.12-slim

WORKDIR /app

# Install deps first for better layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY build_vector_db.py .
COPY couch_db_client.py .
COPY utils.py .

CMD ["python", "build_vector_db.py"]