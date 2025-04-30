FROM python:3.8-slim

# Set working directory
WORKDIR /app

# Copy requirements.txt first for better caching
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Storage Service code
COPY storage_service /app/storage_service

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the consumer
CMD ["python", "storage_service/consumer.py"]