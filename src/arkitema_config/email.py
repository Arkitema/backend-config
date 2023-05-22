from enum import Enum

from requests import Response
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

try:
    from core.config import settings
except (ImportError, ModuleNotFoundError):
    from arkitema_config import config

    settings = config.Settings()


async def send_email(
    recipient: str,
    subject: str,
    message_body: str = "",
    html_body: str | None = None,
) -> Response:
    """
    Send an email invitation to the LCA Platform using Sendgrid

    Parameters
    ----------
    recipient: str
        email address of recipient
    subject: str
        email subject
    message_body: str
        custom text email body
    html_body: str = None,
        not required custom html email body
    """
    if html_body:
        message_body = html_body

    message = Mail(
        from_email=settings.EMAIL_NOTIFICATION_FROM,
        to_emails=recipient,
        subject=subject,
        html_content=message_body,
    )
    try:
        sg = SendGridAPIClient(settings.SENDGRID_SECRET)

        response = sg.send(message)
    except Exception as e:
        response = e.body

    return response
