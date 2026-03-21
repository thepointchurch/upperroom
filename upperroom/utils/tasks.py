import logging

from django.core import mail
from django.tasks import task

logger = logging.getLogger(__name__)


@task
def send_email(subject: str, body: str, from_email: str, to: list[str], test: bool = False) -> None:
    message = mail.EmailMessage(
        subject=subject,
        body=body,
        from_email=from_email,
        to=to,
    )
    if test:
        connection = mail.get_connection(backend="django.core.mail.backends.console.EmailBackend")
    else:
        connection = mail.get_connection()
    connection.send_messages([message])
    for recipient in message.to:
        logger.info("Sent mail to <%s>: %s", recipient, message.subject)
