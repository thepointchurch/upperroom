from datetime import date
from io import BytesIO

from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.files.storage import default_storage
from django.template.loader import get_template
from django.utils.dates import MONTHS
from weasyprint import HTML

from .models import Family, Person
from .views import PdfView, PdfViewCompact, PrintView, PrintViewCompact


def generate_pdf(compact=False, output=None, year=None, month=None):
    render_options = {
        "site_name": get_current_site(None).name,
        "contact_email": settings.DIRECTORY_EMAIL,
        "month": MONTHS[month or date.today().month],
        "year": year or date.today().year,
        "families": Family.active_objects.all(),
        "archived_families": Family.archived_objects.all(),
    }
    output_file = PdfViewCompact.FILE_NAME
    template = PrintViewCompact.template_name
    if not compact:
        render_options["birthdays"] = Person.current_objects.exclude(birthday__isnull=True).only(
            "name", "suffix", "surname_override", "family__name", "birthday"
        )
        render_options["anniversaries"] = (
            Family.current_objects.filter(anniversary__isnull=False)
            .filter(husband__isnull=False, husband__is_current=True)
            .filter(wife__isnull=False, wife__is_current=True)
            .prefetch_related(None)
            .only(
                "name",
                "husband__name",
                "husband__suffix",
                "husband__surname_override",
                "wife__name",
                "wife__suffix",
                "wife__surname_override",
                "anniversary",
            )
        )
        output_file = PdfView.FILE_NAME
        template = PrintView.template_name
    html = get_template(template).render(render_options)
    pdf_data = HTML(string=html, encoding="utf-8").write_pdf()

    if output:
        with open(output, "wb") as pdf:
            pdf.write(pdf_data)
    else:
        pdf = BytesIO()
        pdf.write(pdf_data)
        if default_storage.exists(output_file):
            default_storage.delete(output_file)
        default_storage.save(output_file, pdf)
        pdf.close()
