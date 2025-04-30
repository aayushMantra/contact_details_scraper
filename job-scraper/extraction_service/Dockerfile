# extraction_service/Dockerfile
FROM python:3.8-slim

# Set working directory
WORKDIR /app

# Copy the Extraction Service code
COPY extraction_service /app/extraction_service

COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the consumer
CMD ["python", "extraction_service/consumer.py"]