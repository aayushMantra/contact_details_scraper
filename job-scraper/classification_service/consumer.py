# classification_service/consumer.py
import pika
import json
import time
from config import RABBITMQ_HOST, RABBITMQ_PORT, RABBITMQ_CLASSIFY_QUEUE, RABBITMQ_EXCHANGE,RABBITMQ_EXTRACT_QUEUE, logger
from downloader import download_page
from classifier import JobPostingClassifier
from prometheus_client import start_http_server

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
                    pika.ConnectionParameters(host=self.host, port=self.port, heartbeat=30, blocked_connection_timeout=300)
                )
                self.channel = self.connection.channel()
                self.channel.queue_declare(queue=self.queue, durable=True)
                logger.info(f"Producer connected to RabbitMQ at {self.host}:{self.port}, queue: {self.queue}")
                return
            except Exception as e:
                attempt += 1
                logger.error(f"Producer failed to connect to RabbitMQ (attempt {attempt}/{max_retries}): {e}")
                if attempt == max_retries:
                    raise Exception("Max retries reached. Producer could not connect to RabbitMQ.")
                time.sleep(retry_interval)

    def publish(self, message):
        try:
            self.channel.basic_publish(
                exchange=self.exchange,
                routing_key=self.queue,
                body=json.dumps(message).encode(),
                properties=pika.BasicProperties(delivery_mode=2)  # Make message persistent
            )
            logger.info(f"Published message to {self.queue}: {json.dumps(message)}")
        except Exception as e:
            logger.error(f"Failed to publish message to {self.queue}: {e}")
            raise

    def close(self):
        if self.connection and not self.connection.is_closed:
            self.connection.close()

class RabbitMQConsumer:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.producer = RabbitMQProducer(RABBITMQ_HOST, RABBITMQ_PORT, RABBITMQ_EXTRACT_QUEUE)
        self.classifier = JobPostingClassifier()
        self.connect()

    def connect(self, max_retries=5, retry_interval=5):
        attempt = 0
        while attempt < max_retries:
            try:
                self.connection = pika.BlockingConnection(
                    pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT, heartbeat=30, blocked_connection_timeout=300)
                )
                self.channel = self.connection.channel()
                self.channel.queue_declare(queue=RABBITMQ_CLASSIFY_QUEUE, durable=True)
                logger.info(f"Consumer connected to RabbitMQ at {RABBITMQ_HOST}:{RABBITMQ_PORT}, queue: {RABBITMQ_CLASSIFY_QUEUE}")
                # Initialize the producer for the urls_to_extract queue
                self.producer = RabbitMQProducer(
                    host=RABBITMQ_HOST,
                    port=RABBITMQ_PORT,
                    queue=RABBITMQ_EXTRACT_QUEUE,
                    exchange= RABBITMQ_EXCHANGE
                )
                return
            except Exception as e:
                attempt += 1
                logger.error(f"Consumer failed to connect to RabbitMQ (attempt {attempt}/{max_retries}): {e}")
                if attempt == max_retries:
                    raise Exception("Max retries reached. Consumer could not connect to RabbitMQ.")
                time.sleep(retry_interval)

    def callback(self, ch, method, properties, body):
        try:
            # Parse the message
            try:
                message = json.loads(body)
                if isinstance(message, str):
                    message = json.loads(message)
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {e}")
                logger.error(f"Message body: {body}")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
                return
                
            url = message.get("url")
            if not url:
                logger.warning("Received message with no URL, skipping")
                ch.basic_ack(delivery_tag=method.delivery_tag)
                return

            print(f"Processing URL: {url}")
            # Download the page content
            html_content = download_page(url)
            if not html_content:
                logger.warning(f"Failed to download content for {url}")
                ch.basic_ack(delivery_tag=method.delivery_tag)
                return

            # Classify the page (from Sub-Step 3.2)
            is_job_posting, reason = self.classifier.classify_page(url, html_content)
            logger.info(f"Classified {url} as a job posting: {reason}")
            
            if is_job_posting:
                # Publish to urls_to_extract queue
                self.producer.publish(json.dumps({"url": url}))
                logger.info(f"Sent {url} to extraction queue")
            else:
                logger.info(f"Classified {url} as not a job posting: {reason}")

            # Acknowledge the message
            ch.basic_ack(delivery_tag=method.delivery_tag)
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            # Requeue the message if processing fails
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    def start_consuming(self):
        logger.info(f"Starting consumer for queue: {RABBITMQ_CLASSIFY_QUEUE}")
        self.channel.basic_qos(prefetch_count=1)  # Process one message at a time
        self.channel.basic_consume(queue=RABBITMQ_CLASSIFY_QUEUE, on_message_callback=self.callback)
        self.channel.start_consuming()

    def close(self):
        if self.producer:
            self.producer.close()
        if self.connection and not self.connection.is_closed:
            self.connection.close()

if __name__ == "__main__":
    start_http_server(8002)  # Expose metrics on port 8002
    consumer = None
    try:
        consumer = RabbitMQConsumer()
        consumer.start_consuming()
    except KeyboardInterrupt:
        print("Stopping consumer...")
        if consumer:
            consumer.close()
    except Exception as e:
        print(f"Consumer error: {e}")
        if consumer:
            consumer.close()