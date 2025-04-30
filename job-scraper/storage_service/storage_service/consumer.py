# job-scraper/storage_service/consumer.py
import pika
import json
import time
from config import RABBITMQ_HOST, RABBITMQ_PORT, RABBITMQ_STORE_QUEUE, RABBITMQ_EXCHANGE, logger, DEFAULT_VALUES
from prometheus_client import Counter, Summary
from data_processor import DataProcessor

# Prometheus Metrics
JOBS_RECEIVED = Counter('jobs_received_total', 'Total number of jobs received from queue')
PROCESSING_TIME = Summary('processing_time_total', 'Total time spent processing jobs')

class RabbitMQConsumer:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.processor = DataProcessor()
        self.connect()

    def connect(self, max_retries=5, retry_interval=5):
        attempt = 0
        while attempt < max_retries:
            try:
                self.connection = pika.BlockingConnection(
                    pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT, blocked_connection_timeout=300, heartbeat=30)
                )
                self.channel = self.connection.channel()
                self.channel.queue_declare(queue=RABBITMQ_STORE_QUEUE, durable=True)
                logger.info(f"Connected to RabbitMQ at {RABBITMQ_HOST}:{RABBITMQ_PORT}, queue: {RABBITMQ_STORE_QUEUE}")
                return
            except Exception as e:
                attempt += 1
                logger.error(f"Failed to connect to RabbitMQ (attempt {attempt}/{max_retries}): {e}")
                if attempt == max_retries:
                    raise
                time.sleep(retry_interval)

    def parse_job_data(self, body):
        """
        Parse the JSON data received from the queue.
        Args:
            body (bytes): The raw message body from RabbitMQ.
        Returns:
            dict or None: Parsed job data or None if parsing fails.
        """
        try:
            job_data = json.loads(body)
            logger.info(f"Parsed job data: {json.dumps(job_data, indent=2)}")
            required_fields = {"title", "company", "location", "description", "url", "source"}
            if not all(field in job_data for field in required_fields):
                missing = required_fields - set(job_data.keys())
                logger.warning(f"Missing fields in job data: {missing}")
                return None
            return job_data
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON data: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error parsing job data: {e}")
            return None

    def callback(self, ch, method, properties, body):
        with PROCESSING_TIME.time():  # Using Histogram for timing (requires prometheus_client update)
            start_time = time.time()
            try:
                logger.info(f"Received raw message: {body.decode()}")
                job_data = self.parse_job_data(body)
                if job_data:
                    JOBS_RECEIVED.inc()
                    logger.info(f"Successfully processed job data from URL: {job_data.get('url')}")
                    cleaned_data = self.processor.process_data(job_data)
                    logger.info(f"Cleaned and normalized job data: {json.dumps(cleaned_data, indent=2)}")
                    # Placeholder for storage logic (to be implemented in next substeps)
                    logger.info("Job data ready for storage (placeholder)")
                else:
                    logger.warning("Discarding malformed job data")

                ch.basic_ack(delivery_tag=method.delivery_tag)
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    def start_consuming(self):
        logger.info(f"Starting consumer for queue: {RABBITMQ_STORE_QUEUE}")
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(queue=RABBITMQ_STORE_QUEUE, on_message_callback=self.callback)
        self.channel.start_consuming()

    def close(self):
        if self.connection and not self.connection.is_closed:
            self.connection.close()

if __name__ == "__main__":
    from prometheus_client import start_http_server
    start_http_server(8004)  # Expose metrics on port 8004
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