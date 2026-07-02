
from aiokafka import AIOKafkaProducer
import json
import logging

logger = logging.getLogger(__name__)


producer: AIOKafkaProducer = None


async def start_producer():
    """Start the Kafka producer. Called on app startup."""
    global producer
    producer = AIOKafkaProducer(
        bootstrap_servers="localhost:9092",  
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),  
    )
    await producer.start()
    logger.info("✅ Kafka producer started")


async def stop_producer():
    """Stop the Kafka producer. Called on app shutdown."""
    global producer
    if producer:
        await producer.stop()
        logger.info("🛑 Kafka producer stopped")


async def publish_event(topic: str, event: dict):
  
    if not producer:
        logger.warning("Kafka producer not started — skipping event")
        return
    try:
        await producer.send_and_wait(topic, event)
        logger.info(f"📨 Event published to '{topic}': {event}")
    except Exception as e:
        logger.error(f"Failed to publish event to '{topic}': {e}")