# Use Python slim base image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies for Playwright
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    curl \
    libglib2.0-0 \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxkbcommon0 \
    libx11-6 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    libatspi2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install chromium && \
    playwright install-deps chromium

# Copy the application code
COPY . /app/

# Ensure output directory exists
RUN mkdir -p /app/output

# Create an empty CSV file if it doesn't exist
RUN touch /app/output/contact_data.csv

# Add path to system path
RUN echo '#!/usr/bin/env python3\n\
import sys\n\
original_path = sys.path.copy()\n\
if "/app" not in sys.path:\n\
    sys.path.insert(0, "/app")\n\
print("Contact service path added: /app")' > /usr/local/bin/update_path.py && \
    chmod +x /usr/local/bin/update_path.py

# Command to run the spider
CMD ["sh", "-c", "python3 /usr/local/bin/update_path.py && scrapy crawl contact_spider"]
