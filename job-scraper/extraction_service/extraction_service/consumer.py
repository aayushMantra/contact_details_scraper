# extraction_service/extraction_service/consumer.py
import pika
import json
import time
from config import RABBITMQ_HOST, RABBITMQ_PORT, RABBITMQ_EXTRACT_QUEUE, RABBITMQ_EXCHANGE, RABBITMQ_STORE_QUEUE, logger
from extractor import JobExtractor
from prometheus_client import Counter, Histogram

# Prometheus Metrics
JOB_POSTINGS_EXTRACTED = Counter('job_postings_extracted_total', 'Total number of job postings extracted')
EXTRACTION_TIME = Histogram('extraction_time_seconds', 'Time spent extracting job postings')
EXTRACTION_SUCCESS = Counter('extraction_success_total', 'Number of successful extractions', ['status'])

class RabbitMQProducer:
    def __init__(self, host, port, queue, exchange=''):
        self.host = host
        self.port = port
        self.queue = queue
        self.exchange = exchange
        self.connection = None
        self.channel = None
        self.connect()

    def connect(self, max_retries=5, retry_interval=5):
        attempt = 0
        while attempt < max_retries:
            try:
                self.connection = pika.BlockingConnection(
                    pika.ConnectionParameters(host=self.host, port=self.port, blocked_connection_timeout=300, heartbeat=30)
                )
                self.channel = self.connection.channel()
                self.channel.queue_declare(queue=self.queue, durable=True)
                logger.info(
                    f"Producer connected to RabbitMQ at {self.host}:{self.port}, queue: {self.queue}")
                return
            except Exception as e:
                attempt += 1
                logger.error(
                    f"Producer failed to connect to RabbitMQ (attempt {attempt}/{max_retries}): {e}")
                if attempt == max_retries:
                    raise Exception(
                        f"Max retries reached. Producer could not connect to {self.queue}.")
                time.sleep(retry_interval)

    def publish(self, message):
        try:
            logger.info(f"Attempting to publish to {self.queue}: {json.dumps(message)}")
            self.channel.basic_publish(
                exchange=self.exchange,
                routing_key=self.queue,
                body=json.dumps(message).encode(),
                properties=pika.BasicProperties(
                    delivery_mode=2)  # Make message persistent
            )
            logger.info(f"Published data to {self.queue}: {json.dumps(message)}")
        except Exception as e:
            logger.error(f"Failed to publish data to {self.queue}: {e}")
            raise

    def close(self):
        if self.connection and not self.connection.is_closed:
            self.connection.close()

class RabbitMQConsumer:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.extractor = JobExtractor()
        self.producer = RabbitMQProducer(RABBITMQ_HOST, RABBITMQ_PORT, RABBITMQ_STORE_QUEUE)
        self.connect()

    def connect(self, max_retries=5, retry_interval=5):
        attempt = 0
        while attempt < max_retries:
            try:
                self.connection = pika.BlockingConnection(
                    pika.ConnectionParameters(
                        host=RABBITMQ_HOST, port=RABBITMQ_PORT, blocked_connection_timeout=300, heartbeat=30)
                )
                self.channel = self.connection.channel()
                self.channel.queue_declare(queue=RABBITMQ_EXTRACT_QUEUE, durable=True)
                logger.info(
                    f"Connected to RabbitMQ at {RABBITMQ_HOST}:{RABBITMQ_PORT}, queue: {RABBITMQ_EXTRACT_QUEUE}")
                return
            except Exception as e:
                attempt += 1
                logger.error(
                    f"Failed to connect to RabbitMQ (attempt {attempt}/{max_retries}): {e}")
                if attempt == max_retries:
                    raise Exception(
                        "Max retries reached. Could not connect to RabbitMQ.")
                time.sleep(retry_interval)

    def callback(self, ch, method, properties, body):
        try:
            # Check if body is empty
            if not body or len(body) == 0:
                logger.info("Received empty message, acknowledging and skipping")
                ch.basic_ack(delivery_tag=method.delivery_tag)
                return

            try:
                # Parse the message
                message = json.loads(body)
                
                if isinstance(message, str):
                    message = json.loads(message)
                    
            except json.JSONDecodeError as e:
                logger.error(f"Received invalid JSON: {body[:100]}... Error: {e}")
                # Acknowledge the message since we can't process it
                ch.basic_ack(delivery_tag=method.delivery_tag)
                return

            url = message.get("url")
            if not url:
                logger.warning("Received message with no URL, skipping")
                ch.basic_ack(delivery_tag=method.delivery_tag)
                return

            logger.info(f"Received URL for extraction: {url}")

            # Extract job data
            job_data = self.extractor.extract_job_data(url)
            if job_data:
                logger.info(f"Extracted job data before publish: {json.dumps(job_data, indent=2)}")
                self.producer.publish(job_data)
                logger.info(f"Published data to {RABBITMQ_STORE_QUEUE}")
                logger.info(f"Processing URL: {url}")
            else:
                logger.info(f"No job data extracted from {url}")

            # Placeholder for extraction logic (to be implemented in Sub-Step 3.5)
            # self.process_url(url)

            # Acknowledge the message
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            # Log the message body for debugging
            logger.error(f"Message body: {body[:100]}...")
            # Requeue the message if processing fails
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    # def process_url(self, url):
    #     """
    #     Placeholder method for URL processing (e.g., downloading and extracting data).
    #     To be implemented in Sub-Step 3.5.
    #     """
    #     print(f"Processing URL (placeholder): {url}")

    def start_consuming(self):
        logger.info(f"Starting consumer for queue: {RABBITMQ_EXTRACT_QUEUE}")
        # Process one message at a time
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(
            queue=RABBITMQ_EXTRACT_QUEUE, on_message_callback=self.callback)
        self.channel.start_consuming()

    def close(self):
        if self.connection and not self.connection.is_closed:
            self.connection.close()


if __name__ == "__main__":
    consumer = None
    try:
        consumer = RabbitMQConsumer()
        consumer.start_consuming()
    except KeyboardInterrupt:
        logger.info("Stopping consumer...")
        if consumer:
            consumer.close()
    except Exception as e:
        logger.error(f"Consumer error: {e}")
        if consumer:
            consumer.close()
