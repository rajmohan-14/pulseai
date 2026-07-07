
import asyncio
import json
import logging
from aiokafka import AIOKafkaConsumer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def handle_event(event: dict):
    event_type = event.get("type")

    if event_type == "user_registered":
        logger.info(f"🎉 New user registered: {event.get('email')}")

       
        from app.core.ai_client import classify_event
        classification = await classify_event(event)
        event["classification"] = classification
        logger.info(f"🤖 Classified as: {classification}")

        
        from app.core.vector_store import store_event
        await store_event(event)

       
        from app.tasks.notification_tasks import (
            send_welcome_email,
            notify_admin_new_user,
        )
        send_welcome_email.delay(
            user_id=event.get("user_id"),
            email=event.get("email"),
            username=event.get("username"),
        )
        notify_admin_new_user.delay(
            user_id=event.get("user_id"),
            email=event.get("email"),
            role=event.get("role"),
        )
        logger.info(f"✅ AI processed and Celery tasks triggered")

    elif event_type == "user_login":
        logger.info(f"🔑 User logged in: {event.get('email')}")

     
        from app.core.ai_client import classify_event
        from app.core.vector_store import store_event
        classification = await classify_event(event)
        event["classification"] = classification
        await store_event(event)

    else:
        logger.info(f"📨 Unknown event: {event.get('type')}")

async def consume_events():
    logger.info("🚀 Starting Kafka consumer...")

    consumer = AIOKafkaConsumer(
        "user-events",
        bootstrap_servers="localhost:9092",
        group_id="pulseai-consumer-group",
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        auto_offset_reset="earliest",
    )

    for attempt in range(10):
        try:
            await consumer.start()
            logger.info("✅ Kafka consumer started. Listening for events...")
            break
        except Exception as e:
            logger.warning(f"Kafka not ready (attempt {attempt+1}/10) — retrying in 5s...")
            await asyncio.sleep(5)
    else:
        logger.error("❌ Could not connect to Kafka after 10 attempts")
        return

    try:
        async for message in consumer:
            logger.info(f"📬 Event received from '{message.topic}'")
            await handle_event(message.value)
    except Exception as e:
        logger.error(f"Consumer error: {e}")
    finally:
        await consumer.stop()
    await consumer.start()
    logger.info("✅ Kafka consumer started. Listening for events...")

    try:
        async for message in consumer:
            logger.info(f"📬 Event received from '{message.topic}'")
            await handle_event(message.value)
    except Exception as e:
        logger.error(f"Consumer error: {e}")
    finally:
        await consumer.stop()


if __name__ == "__main__":
    asyncio.run(consume_events())