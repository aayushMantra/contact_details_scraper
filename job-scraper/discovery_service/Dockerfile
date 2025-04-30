# discovery_service/Dockerfile
FROM python:3.12

# Set working directory
WORKDIR /app

# Create a virtual environment
RUN python3 -m pip install --upgrade pip && \
    python3 -m pip install virtualenv && \
    python3 -m virtualenv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install
COPY requirements.txt /app/

RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the project
COPY . /app/

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=UTF-8
ENV LANG=C.UTF-8

# Add path to system path
RUN echo '#!/bin/bash\n\
import sys\n\
original_path = sys.path.copy()\n\
print(f"Initial sys.path: {original_path}")\n\
if "/app" not in sys.path:\n\
    sys.path.insert(0, "/app")\n\
print(f"Updated sys path: {sys.path}")\n\
print("Discovery service path added: /app")' > /usr/local/bin/update_path.py && \
    chmod +x /usr/local/bin/update_path.py

# Create a start script
RUN echo '#!/bin/bash\n\
python3 /usr/local/bin/update_path.py\n\
cd /app/job_scraper && scrapy crawl job_spider\n' > /usr/local/bin/start_spider.sh && \
    chmod +x /usr/local/bin/start_spider.sh

# Verify the project structure
RUN ls -la /app && ls -la /app/job_scraper

# Set the working directory
WORKDIR /app

# Set the command to run the spider
CMD ["/usr/local/bin/start_spider.sh"]