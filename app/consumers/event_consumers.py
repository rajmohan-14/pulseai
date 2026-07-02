
import asyncio
import json
import logging
from aiokafka import AIOKafkaConsumer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def handle_event(event: dict):
    
    event_type = event.get("type")

    if event_type == "user_registered":
        logger.info(f"🎉 New user registered!")
        logger.info(f"   User ID  : {event.get('user_id')}")
        logger.info(f"   Email    : {event.get('email')}")
        logger.info(f"   Username : {event.get('username')}")
        logger.info(f"   Role     : {event.get('role')}")
      

    elif event_type == "user_login":
        logger.info(f"🔑 User logged in!")
        logger.info(f"   User ID  : {event.get('user_id')}")
        logger.info(f"   Email    : {event.get('email')}")
        

    else:
        logger.info(f"📨 Unknown event type: {event_type}")


async def consume_events():
   
    logger.info("🚀 Starting Kafka consumer...")

    consumer = AIOKafkaConsumer(
        "user-events",                          
        bootstrap_servers="localhost:9092",      
        group_id="pulseai-consumer-group",       
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),  
        auto_offset_reset="earliest",        
    )

    await consumer.start()
    logger.info("✅ Kafka consumer started. Listening for events...")

    try:
       
        async for message in consumer:
            logger.info(f"📬 Event received from topic '{message.topic}'")
            await handle_event(message.value)

    except Exception as e:
        logger.error(f"Consumer error: {e}")
    finally:
        await consumer.stop()
        logger.info("🛑 Kafka consumer stopped")


if __name__ == "__main__":
    
    asyncio.run(consume_events())