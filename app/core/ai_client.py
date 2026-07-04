
import logging
from groq import Groq
from app.core.config import settings

logger = logging.getLogger(__name__)


_client: Groq = None


def get_llm_client() -> Groq:
  
    global _client
    if _client is None:
        _client = Groq(api_key=settings.GROQ_API_KEY)
    return _client


async def classify_event(event: dict) -> str:
 
    client = get_llm_client()

    event_text = f"Event type: {event.get('type')}, Data: {event}"

    prompt = f"""You are an event classifier for a backend system.
Classify the following event into exactly one category: critical, warning, or info.


Event: {event_text}

Respond with ONLY one word: critical, warning, or info."""

    try:
        response = client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=10,      
            temperature=0,      
        )
        classification = response.choices[0].message.content.strip().lower()


        if classification not in ["critical", "warning", "info"]:
            classification = "info" 

        logger.info(f"🤖 Event classified as: {classification}")
        return classification

    except Exception as e:
        logger.error(f"LLM classification failed: {e}")
        return "info" 


async def generate_answer(question: str, context_events: list) -> str:

    client = get_llm_client()


    context = "\n".join([
        f"- [{e.get('type', 'unknown')}] {e.get('email', '')} at {e.get('timestamp', '')}"
        for e in context_events
    ])

    prompt = f"""You are an AI assistant for PulseAI, a backend monitoring system.
Answer the user's question based ONLY on the provided events.
Be concise and specific.

Recent system events:
{context}

Question: {question}

Answer:"""

    try:
        response = client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.3,
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        logger.error(f"LLM answer generation failed: {e}")
        return "Sorry, I couldn't generate an answer right now."


async def summarize_events(events: list) -> str:
    
    client = get_llm_client()

    events_text = "\n".join([
        f"- {e.get('type', 'unknown')}: {e.get('email', 'system')} at {e.get('timestamp', '')}"
        for e in events
    ])

    prompt = f"""Summarize these system events in 2-3 sentences for a developer dashboard.
Be specific about counts and patterns.

Events:
{events_text}

Summary:"""

    try:
        response = client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
            temperature=0.3,
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        logger.error(f"LLM summarization failed: {e}")
        return "Could not generate summary."