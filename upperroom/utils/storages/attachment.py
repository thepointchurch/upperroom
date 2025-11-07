from django.conf import settings
from django.core.files.storage import default_storage
from django.http import FileResponse, HttpResponseRedirect
from django.utils.http import content_disposition_header


def attachment_response(file_obj, as_attachment=True, filename="", content_type=None):
    file_storage = getattr(file_obj, "storage", None)
    if file_storage and hasattr(file_storage, "bucket"):
        parameters = {}
        if as_attachment and filename:
            parameters["ResponseContentDisposition"] = content_disposition_header(True, filename)
        if content_type:
            parameters["ResponseContentType"] = content_type
        url = default_storage.url(getattr(file_obj, "name", file_obj), parameters=parameters)
        return HttpResponseRedirect(url)
    if isinstance(file_obj, str):
        file_obj = open(f"{settings.MEDIA_ROOT}/{file_obj}", "rb")  # pylint: disable=consider-using-with
    return FileResponse(file_obj, as_attachment=as_attachment, filename=filename, content_type=content_type)
