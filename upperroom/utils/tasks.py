import logging

from django.core import mail
from django.tasks import task

logger = logging.getLogger(__name__)


@task
def send_email(subject: str, body: str, from_email: str, to: list[str]) -> None:
    message = mail.EmailMessage(
        subject=subject,
        body=body,
        from_email=from_email,
        to=to,
    )
    message.send()
    for recipient in message.to:
        logger.info("Sent mail to <%s>: %s", recipient, message.subject)
