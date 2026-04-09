"""
WhatsApp notification provider abstraction.

Supports multiple backends via WHATSAPP_PROVIDER env var:
  - "meta"    → Meta Cloud API (default, requires WHATSAPP_API_TOKEN + WHATSAPP_PHONE_NUMBER_ID)
  - "twilio"  → Twilio WhatsApp (requires TWILIO_ACCOUNT_SID + TWILIO_AUTH_TOKEN + TWILIO_WHATSAPP_FROM)
  - "console" → Prints to console (development/testing)

Usage:
    from apps.notifications.whatsapp import send_whatsapp
    success, info = send_whatsapp("+5215512345678", "Hola!")
"""
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


def send_whatsapp(phone_number: str, message: str) -> tuple[bool, str]:
    """
    Send a WhatsApp message. Returns (success: bool, info: str).
    Phone number must include country code, e.g. "5215512345678" (no +).
    """
    provider = getattr(settings, "WHATSAPP_PROVIDER", "console")

    if provider == "meta":
        return _send_via_meta(phone_number, message)
    elif provider == "twilio":
        return _send_via_twilio(phone_number, message)
    else:
        return _send_via_console(phone_number, message)


# ---------------------------------------------------------------------------
# Meta Cloud API
# ---------------------------------------------------------------------------
def _send_via_meta(phone: str, message: str) -> tuple[bool, str]:
    import requests

    token = getattr(settings, "WHATSAPP_API_TOKEN", "")
    phone_id = getattr(settings, "WHATSAPP_PHONE_NUMBER_ID", "")

    if not token or not phone_id:
        logger.warning("Meta WhatsApp API not configured (missing token or phone_id)")
        return False, "Meta WhatsApp API not configured"

    url = f"https://graph.facebook.com/v18.0/{phone_id}/messages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": phone,
        "type": "text",
        "text": {"body": message},
    }
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=10)
        resp.raise_for_status()
        return True, resp.json().get("messages", [{}])[0].get("id", "sent")
    except Exception as e:
        logger.error("Meta WhatsApp send failed: %s", e)
        return False, str(e)


# ---------------------------------------------------------------------------
# Twilio WhatsApp
# ---------------------------------------------------------------------------
def _send_via_twilio(phone: str, message: str) -> tuple[bool, str]:
    sid = getattr(settings, "TWILIO_ACCOUNT_SID", "")
    token = getattr(settings, "TWILIO_AUTH_TOKEN", "")
    from_number = getattr(settings, "TWILIO_WHATSAPP_FROM", "")

    if not sid or not token or not from_number:
        logger.warning("Twilio not configured (missing SID, token or from number)")
        return False, "Twilio not configured"

    try:
        from twilio.rest import Client
        client = Client(sid, token)
        msg = client.messages.create(
            body=message,
            from_=f"whatsapp:{from_number}",
            to=f"whatsapp:+{phone}",
        )
        return True, msg.sid
    except ImportError:
        return False, "twilio package not installed (pip install twilio)"
    except Exception as e:
        logger.error("Twilio WhatsApp send failed: %s", e)
        return False, str(e)


# ---------------------------------------------------------------------------
# Console (development)
# ---------------------------------------------------------------------------
def _send_via_console(phone: str, message: str) -> tuple[bool, str]:
    print(f"\n{'='*50}")
    print(f"[WhatsApp → {phone}]")
    print(message)
    print("="*50)
    logger.info("WhatsApp (console) → %s: %s", phone, message[:60])
    return True, "console"
