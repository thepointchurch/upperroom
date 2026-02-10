import logging

from django.core import mail
from django.tasks import task

logger = logging.getLogger(__name__)


@task
def send_email(message: mail.EmailMessage) -> None:
    message.send()
    for recipient in message.to:
        logger.info("Sent mail to <%s>: %s", recipient, message.subject)
