from django.tasks import task

from .utils import generate_pdf


@task
def generate_directory_pdf(compact=False, output=None, year=None, month=None):
    return generate_pdf(compact, output, year, month)
