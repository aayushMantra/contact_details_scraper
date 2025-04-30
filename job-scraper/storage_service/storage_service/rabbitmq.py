# import pika
# import json
# import time
# from sqlalchemy.orm import sessionmaker
# from database import JobPosting, engine, save_to_elasticsearch
# from config import RABBITMQ_HOST, RABBITMQ_PORT, RABBITMQ_QUEUE

# # Set up SQLAlchemy session
# Session = sessionmaker(bind=engine)

# class RabbitMQConsumer:
#     def __init__(self):
#         self.connection = None
#         self.channel = None
#         self.connect()

#     def connect(self):
#         max_retries = 10
#         retry_delay = 5
#         for attempt in range(max_retries):
#             try:
#                 self.connection = pika.BlockingConnection(
#                     pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT)
#                 )
#                 self.channel = self.connection.channel()
#                 self.channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)
#                 print("Connected to RabbitMQ")
#                 return
#             except Exception as e:
#                 print(f"Failed to connect to RabbitMQ (attempt {attempt + 1}/{max_retries}): {e}")
#                 if attempt < max_retries - 1:
#                     time.sleep(retry_delay)
#                 else:
#                     raise Exception("Failed to connect to RabbitMQ after maximum retries")

#     def callback(self, ch, method, properties, body):
#         try:
#             job_data = json.loads(body)
#             print(f"Received job posting: {job_data['job_title']}")
#             session = Session()
#             job = JobPosting(
#                 job_title=job_data.get('job_title'),
#                 company=job_data.get('company'),
#                 location=job_data.get('location'),
#                 description=job_data.get('description'),
#                 salary=job_data.get('salary'),
#                 posting_date=job_data.get('posting_date'),
#                 application_url=job_data.get('application_url'),
#                 source=job_data.get('source')
#             )
#             session.add(job)
#             session.commit()
#             print(f"Saved to PostgreSQL: {job_data['job_title']}")
#             save_to_elasticsearch(job_data)
#             ch.basic_ack(delivery_tag=method.delivery_tag)
#         except Exception as e:
#             print(f"Error processing message: {e}")
#             session.rollback()
#             ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

#     def start_consuming(self):
#         self.channel.basic_qos(prefetch_count=1)
#         self.channel.basic_consume(queue=RABBITMQ_QUEUE, on_message_callback=self.callback)
#         print("Storage Service: Waiting for job postings...")
#         self.channel.start_consuming()

#     def close(self):
#         if self.connection and not self.connection.is_closed:
#             self.connection.close()