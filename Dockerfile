FROM python:3.9-slim AS compile-image
RUN apt-get -y update && apt-get install -y --no-install-recommends \
    build-essential gcc python3-dev libpq-dev zlib1g-dev && \
    apt-get clean && rm -rf /var/lib/apt/lists/*
RUN pip install poetry=="1.1.12" wheel
COPY . /django/
WORKDIR /django
ENV POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PYTHONDONTWRITEBYTECODE=1
RUN poetry install --no-dev --no-root -E aws -E cache -E pgsql
RUN poetry build --format wheel && .venv/bin/pip install dist/*.whl
RUN find .venv -type f -name '*.py[co]' -delete -o -type d -name __pycache__ -delete


FROM python:3.9-slim AS build-image
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/django/.venv/bin:$PATH" \
    DJANGO_SETTINGS_MODULE=upperroom.settings
RUN apt-get -y update \
    && apt-get install -y --no-install-recommends \
        bzip2 \
        curl \
        libpq5 \
        libcairo2 \
        libgdk-pixbuf2.0-0 \
        libpango-1.0-0 \
        libpangocairo-1.0-0 \
        mime-support \
        netcat-traditional \
        postgresql-client \
    && apt-get clean && rm -rf /var/lib/apt/lists/* \
    && useradd -md /django -s /bin/bash -u 8000 django \
    && touch /django/.env && chown 0:8000 /django/.env && chmod 640 /django/.env \
    && mkdir -p /django/data && chown 8000:8000 /django/data
COPY --from=compile-image /django/.venv /django/.venv
COPY entrypoint.sh /entrypoint.sh
COPY gunicorn.py /etc/gunicorn.py

EXPOSE 8000/tcp

USER django:django
WORKDIR /django
ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "-b", "0.0.0.0:8000", "--config", "/etc/gunicorn.py", "upperroom.wsgi"]
VOLUME /django/data

HEALTHCHECK --interval=5m --timeout=3s CMD curl -fsS -o /dev/null http://localhost:8000/ || exit 1

ARG version
ARG build_date

LABEL org.label-schema.schema-version="1.0"
LABEL org.label-schema.version="$version"
LABEL org.label-schema.build-date="$build_date"
LABEL org.label-schema.url="https://github.com/thepointchurch/upperroom"
LABEL org.label-schema.description="Upper Room Church Website"
