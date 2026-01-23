from django.tasks import task

from .utils import send_roster_emails as send_emails


@task
def send_roster_emails(notification_date=None, alert_interval=3, test=False):
    return send_emails(notification_date, alert_interval, test)
