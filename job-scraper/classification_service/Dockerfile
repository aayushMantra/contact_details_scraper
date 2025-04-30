# classification_service/Dockerfile
FROM python:3.8-slim

# Set working directory
WORKDIR /app

# Copy the Classification Service code
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the consumer
CMD ["python", "consumer.py"]