import aiosmtplib
from email.message import EmailMessage
import logging

from app.core.config import SMTP_HOST, SMTP_PORT, SENDER_EMAIL

logger = logging.getLogger(__name__)

async def send_welcome_email(recipient_email: str, recipient_name: str):
    msg = EmailMessage()
    msg["Subject"] = "Welcome to Our Application!"
    msg["From"] = SENDER_EMAIL
    msg["To"] = recipient_email
    
    body = f"""
    Hello {recipient_name},

    Welcome to our application! We're thrilled to have you on board.

    If you have any questions, feel free to reach out to our support team.

    Best regards,
    The App Team
    """
    msg.set_content(body)

    try:
        await aiosmtplib.send(
            msg,
            hostname=SMTP_HOST,
            port=SMTP_PORT,
        )
        logger.info(f"Welcome email sent successfully to {recipient_email}")
    except aiosmtplib.SMTPException as e:
        logger.error(f"Failed to send welcome email to {recipient_email}: {e}", exc_info=True)
    except Exception as e:
        logger.error(f"An unexpected error occurred while sending email to {recipient_email}: {e}", exc_info=True)