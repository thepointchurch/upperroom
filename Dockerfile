FROM python:3.12-alpine AS compile-image
RUN apk add --no-cache \
        build-base \
        libffi-dev
RUN pip install --root-user-action=ignore --upgrade pip setuptools && \
    pip install --root-user-action=ignore "poetry~=1.8" wheel
COPY . /django/
WORKDIR /django
ENV POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PYTHONDONTWRITEBYTECODE=1
RUN poetry install --only main --no-root -E aws -E cache -E pgsql \
    && poetry build --format wheel && .venv/bin/pip install --root-user-action=ignore dist/*.whl \
    && find .venv -type f -name '*.py[co]' -delete -o -type d -name __pycache__ -delete


FROM python:3.12-alpine AS build-image
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
COPY gunicorn.py /etc/gunicorn.py
COPY --from=compile-image /django/.venv /django/.venv

EXPOSE 8000/tcp

USER django:django
WORKDIR /django
ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "-b", "[::]:8000", "--config", "/etc/gunicorn.py", "upperroom.wsgi"]
VOLUME /django/data

HEALTHCHECK --interval=5m --timeout=3s CMD curl -fsS -o /dev/null http://localhost:8000/ || exit 1

ARG version
ARG build_date

LABEL org.label-schema.schema-version="1.0"
LABEL org.label-schema.version="$version"
LABEL org.label-schema.build-date="$build_date"
LABEL org.label-schema.url="https://github.com/thepointchurch/upperroom"
LABEL org.label-schema.description="Upper Room Church Website"
