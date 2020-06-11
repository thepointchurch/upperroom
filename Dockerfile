FROM python:3.7-slim AS compile-image
RUN apt-get -y update
RUN apt-get install -y --no-install-recommends \
    build-essential gcc python3-dev libpq-dev
RUN apt-get clean
RUN rm -rf /var/lib/apt/lists/*
RUN python -m venv /opt/venv
ENV PYTHONDONTWRITEBYTECODE 1
ENV PATH="/opt/venv/bin:$PATH"
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt


FROM debian:buster-slim as font-image
RUN sed -i '/^deb http:\/\/deb.debian.org\/debian .* main$/ s/$/ contrib/' /etc/apt/sources.list
RUN apt-get -y update
RUN apt-get install -y --no-install-recommends \
    ca-certificates \
    netbase \
    ttf-mscorefonts-installer
WORKDIR /usr/local/share/fonts
RUN wget -qO - https://github.com/mozilla/Fira/archive/4.106.tar.gz | tar -xvzf - Fira-4.106/otf --strip-components=2
RUN apt-get clean
RUN rm -rf /var/lib/apt/lists/*


FROM python:3.7-slim AS build-image
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PATH="/opt/venv/bin:$PATH"
ENV DJANGO_SETTINGS_MODULE=thepoint.settings
COPY --from=compile-image /opt/venv /opt/venv
COPY --from=font-image /usr/share/fonts/truetype/msttcorefonts /usr/local/share/fonts /usr/local/share/fonts/
COPY entrypoint.sh /entrypoint.sh
COPY . /code/
COPY gunicorn.py /etc/gunicorn.py
RUN pip install --no-deps /code/ && rm -rf /code \
    && apt-get -y update \
    && apt-get install -y --no-install-recommends \
        bzip2 \
        curl \
        netcat-traditional \
        libpq5 \
        libcairo2 \
        libgdk-pixbuf2.0-0 \
        libpango-1.0-0 \
        libpangocairo-1.0-0 \
    && apt-get clean && rm -rf /var/lib/apt/lists/* \
    && useradd -md /django -s /bin/bash django

EXPOSE 8000/tcp

USER django:django
WORKDIR /django
ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "-b", "0.0.0.0:8000", "--config", "/etc/gunicorn.py", "thepoint.wsgi"]

HEALTHCHECK --interval=5m --timeout=3s CMD curl -fsS -o /dev/null http://localhost:8000/ || exit 1

ARG version
ARG build_date

LABEL org.label-schema.schema-version="1.0"
LABEL org.label-schema.version="$version"
LABEL org.label-schema.build-date="$build_date"
LABEL org.label-schema.url="https://github.com/thepointchurch/thepoint"
LABEL org.label-schema.description="The Point Church Website"
