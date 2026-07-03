
import logging
from app.core.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="app.tasks.notification_tasks.send_welcome_email", bind=True, max_retries=3)
def send_welcome_email(self, user_id: int, email: str, username: str):
    """
    Send a welcome email to a newly registered user.

    bind=True    → gives access to `self` (the task instance)
    max_retries=3 → if it fails, retry up to 3 times automatically
    """
    try:
        logger.info(f"📧 Sending welcome email to {email}...")

        # In a real app, you'd use SendGrid, SMTP, etc.
        # For now we simulate it with a log
        # Example with SMTP:
        # send_email(to=email, subject="Welcome to PulseAI!", body="...")

        logger.info(f"✅ Welcome email sent to {email} (user_id={user_id})")
        return {"status": "sent", "email": email}

    except Exception as exc:
        logger.error(f"❌ Failed to send email to {email}: {exc}")
        # Retry after 60 seconds if it fails
        raise self.retry(exc=exc, countdown=60)


@celery_app.task(name="app.tasks.notification_tasks.notify_admin_new_user")
def notify_admin_new_user(user_id: int, email: str, role: str):
    """
    Notify admin when a new user registers.
    In real app: send Slack message, email, or push notification.
    """
    logger.info(f"🔔 Admin notification: New {role} registered — {email} (id={user_id})")
    return {"status": "notified", "user_id": user_id}


@celery_app.task(name="app.tasks.notification_tasks.hourly_event_summary")
def hourly_event_summary():
    """
    Runs every hour via Celery Beat.
    Later (Week 4) this will:
      → fetch last hour's events from DB
      → send to LLM for summarization
      → save summary
    For now, just logs a placeholder.
    """
    logger.info("⏰ Running hourly event summary...")
    logger.info("📊 [Placeholder] Would summarize last hour's events here")
    logger.info("✅ Hourly summary complete")
    return {"status": "complete"}