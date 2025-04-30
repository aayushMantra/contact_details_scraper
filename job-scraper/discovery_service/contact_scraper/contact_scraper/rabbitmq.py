# discovery_service/contact_scraper/contact_scraper/rabbitmq.py
import pika
import json
import logging
from contact_scraper.config import RABBITMQ_HOST, RABBITMQ_PORT, RABBITMQ_QUEUE

logger = logging.getLogger(__name__)

class RabbitMQProducer:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.connect()

    def connect(self):
        try:
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT)
            )
            self.channel = self.connection.channel()
            self.channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)
            logger.info(f"Connected to RabbitMQ at {RABBITMQ_HOST}:{RABBITMQ_PORT}")
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            raise

    def publish(self, message):
        try:
            self.channel.basic_publish(
                exchange="",
                routing_key=RABBITMQ_QUEUE,
                body=json.dumps(message),
                properties=pika.BasicProperties(delivery_mode=2)  # Make message persistent
            )
            logger.info(f"Published message to queue '{RABBITMQ_QUEUE}': {message}")
        except Exception as e:
            logger.error(f"Failed to publish message: {e}")
            self.connect()  # Reconnect and retry
            self.publish(message)

    def close(self):
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            logger.info("RabbitMQ connection closed")