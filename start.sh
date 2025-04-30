#!/bin/bash
# Clean up any existing Chrome instances
pkill -f chrome || true
pkill -f Xvfb || true

# Remove any leftover Chrome data directories
rm -rf /tmp/chrome_data_*

# Start Xvfb
Xvfb :99 -screen 0 1920x1080x24 -ac +extension GLX +render -noreset &
export DISPLAY=:99
sleep 2

# Start Scrapy with the job spider
cd /app && scrapy crawl job_spider