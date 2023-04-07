from django.conf import settings
from django.core.files.storage import default_storage
from django.http import FileResponse, HttpResponseRedirect
from django.utils.http import content_disposition_header

from . import is_s3_encrypted, is_s3_file, is_s3_file_public


def attachment_response(file_obj, as_attachment=True, filename="", content_type=None, signed=True):
    if getattr(default_storage, "offload", False):
        parameters = {}
        if as_attachment and filename:
            parameters["ResponseContentDisposition"] = content_disposition_header(True, filename)
        if content_type:
            parameters["ResponseContentType"] = content_type
        url = default_storage.url(getattr(file_obj, "name", file_obj), parameters=parameters)
        if not signed and is_s3_file(file_obj) and is_s3_file_public(file_obj) and not is_s3_encrypted(file_obj):
            url = url.split("?", 1)[0]  # remove auth query strings
        return HttpResponseRedirect(url)
    if isinstance(file_obj, str):
        file_obj = open(f"{settings.MEDIA_ROOT}/{file_obj}", "rb")  # pylint: disable=consider-using-with
    return FileResponse(file_obj, as_attachment=as_attachment, filename=filename, content_type=content_type)
