# discovery_service/rabbitmq.py
import os
import time
import pika
import json
import logging
from job_scraper.config import RABBITMQ_PORT, RABBITMQ_QUEUE,RABBITMQ_HOST
RABBITMQ_HOST = "rabbitmq"

class RabbitMQProducer:
    def __init__(self):
        # Set up connection parameters
        credentials = pika.PlainCredentials('guest', 'guest')
        parameters = pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            port=RABBITMQ_PORT,
            credentials=credentials
        )
        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)
        self.logger = logging.getLogger(__name__)
        self.connect()

    def connect(self, max_retries=5, retry_interval=5):
        attempt = 0
        # Use env var with fallback
        rabbitmq_host = os.getenv("RABBITMQ_HOST", "rabbitmq")
        while attempt < max_retries:
            try:
                self.logger.info(
                    f"Attempting to connect to RabbitMQ at {rabbitmq_host}:{RABBITMQ_PORT} (attempt {attempt + 1}/{max_retries})")
                self.connection = pika.BlockingConnection(
                    pika.ConnectionParameters(
                        host=rabbitmq_host,
                        port=RABBITMQ_PORT,
                        heartbeat=60,
                        blocked_connection_timeout=300
                    )
                )
                self.channel = self.connection.channel()
                self.channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)
                self.logger.info(
                    f"Connected to RabbitMQ and declared queue: {RABBITMQ_QUEUE}")
                return
            except pika.exceptions.AMQPConnectionError as e:
                attempt += 1
                self.logger.error(
                    f"Failed to connect to RabbitMQ (attempt {attempt}/{max_retries}): {e}")
                if attempt == max_retries:
                    raise
                time.sleep(retry_interval * attempt)  # Exponential backoff
            except Exception as e:
                self.logger.error(
                    f"Unexpected error connecting to RabbitMQ: {e}")
                raise

    def publish(self, message):
        try:
            if not self.connection or self.connection.is_closed:
                self.connect()
            self.channel.basic_publish(
                exchange='',
                routing_key=RABBITMQ_QUEUE,
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2)  # Make message persistent
            )
            self.logger.info(f"Published message: {message}")
        except Exception as e:
            self.logger.error(f"Failed to publish message: {e}")
            self.connect()  # Reconnect on failure
            self.publish(message)  # Retry

    def close(self):
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            self.logger.info("RabbitMQ connection closed")
