FROM python:3.13-alpine AS compile-image
RUN apk add --no-cache \
        build-base \
        linux-headers
COPY --from=ghcr.io/astral-sh/uv:0.10.2-python3.13-alpine /usr/local/bin/uv /usr/local/bin/uvx /bin/
COPY . /django/
WORKDIR /django
ENV PYTHONDONTWRITEBYTECODE=1 \
    UV_NO_DEV=1
RUN uv build --wheel \
    && uv sync --locked --extra aws --extra cache --extra pgsql \
    && uv pip install dist/*.whl \
    && find .venv -type f -name '*.py[co]' -delete -o -type d -name __pycache__ -delete

FROM python:3.13-alpine AS build-image
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/django/.venv/bin:$PATH" \
    DJANGO_SETTINGS_MODULE=upperroom.settings
RUN apk add --no-cache \
        bash \
        bzip2 \
        cairo \
        curl \
        gdk-pixbuf \
        libffi \
        netcat-openbsd \
        pango \
        postgresql-client \
        shared-mime-info \
        tzdata \
    && adduser -D -h /django -s /sbin/nologin -u 8000 -g "Django User" django \
    && touch /django/.env && chown 0:8000 /django/.env && chmod 640 /django/.env \
    && mkdir -p /django/data && chown 8000:8000 /django/data
COPY entrypoint.sh /entrypoint.sh
COPY uwsgi.ini /etc/uwsgi.ini
COPY --from=compile-image /django/.venv /django/.venv

EXPOSE 8000/tcp

USER django:django
WORKDIR /django
ENTRYPOINT ["/entrypoint.sh"]
CMD ["uwsgi", "--ini", "/etc/uwsgi.ini"]
VOLUME /django/data

HEALTHCHECK --interval=5m --timeout=3s CMD uwsgi_curl localhost:8000 >/dev/null || exit 1

ARG version
ARG build_date

LABEL org.label-schema.schema-version="1.0"
LABEL org.label-schema.version="$version"
LABEL org.label-schema.build-date="$build_date"
LABEL org.label-schema.url="https://github.com/thepointchurch/upperroom"
LABEL org.label-schema.description="Upper Room Church Website"
