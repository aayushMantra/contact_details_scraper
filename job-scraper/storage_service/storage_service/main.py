from fastapi import FastAPI
from rabbitmq import RabbitMQConsumer
import threading
from prometheus_client import Counter, start_http_server

app = FastAPI(title="Storage Service")

messages_processed = Counter('messages_processed_total', 'Total number of messages processed')

@app.on_event("startup")
async def startup_event():
    consumer = RabbitMQConsumer()
    thread = threading.Thread(target=consumer.start_consuming)
    thread.start()

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

start_http_server(8004)