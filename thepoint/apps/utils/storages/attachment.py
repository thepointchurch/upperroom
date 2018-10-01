from django.conf import settings
from django.core.files.storage import default_storage
from django.http import HttpResponseRedirect, FileResponse


def attachment_response(file_obj, as_attachment=True, filename='', content_type=None):
    if getattr(default_storage, 'offload', False):
        parameters = {}
        if as_attachment and filename:
            parameters['ResponseContentDisposition'] = 'attachment; filename="%s"' % filename
        if content_type:
            parameters['ResponseContentType'] = content_type
        return HttpResponseRedirect(default_storage.url(getattr(file_obj, 'name', file_obj),
                                                        parameters=parameters))
    else:
        if isinstance(file_obj, str):
            file_obj = open('%s/%s' % (settings.MEDIA_ROOT, file_obj), 'rb')
        return FileResponse(file_obj,
                            as_attachment=as_attachment,
                            filename=filename,
                            content_type=content_type)


def attachment_url(url, path, absolute=False, request=None):
    if getattr(default_storage, 'offload', False):
        url = default_storage.url(path)
        url = url.split('?', 1)[0]  # remove auth query strings, should be public
        if not url.startswith('http'):
            url = 'https:' + url
        return url
    else:
        if absolute and request:
            return request.build_absolute_uri(url)
        else:
            return url
