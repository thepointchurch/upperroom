![Release](https://github.com/thepointchurch/upperroom/workflows/Release/badge.svg)
![Docker Image](https://github.com/thepointchurch/upperroom/workflows/Docker%20Image/badge.svg)

# Upper Room #

Upper Room is a framework for church websites.

## Development

To set up a development environment:

1. [Install uv](https://docs.astral.sh/uv/getting-started/installation/)

2. Clone the `testing` repository:

    ```
    git clone -branch testing https://github.com/thepointchurch/upperroom.git
    cd upperroom
    ```

3. Set up the virtual environment:

    ```
    uv sync --locked --all-extras --dev
    uv run pre-commit install
    ```

4. Set config variables:

    ```
    cat >.env <<DEV_ENV
    DEBUG=on
    DATABASE_URL='sqlite:///upperroom.sqlite3'
    SECRET_KEY='12345678'
    DJANGO_SETTINGS_MODULE=upperroom.settings
    DEV_ENV
    ```

5. Initialise the database:

    ```
    uv run --env-file .env -- upperroom migrate
    ```

6. Start a test server:

    ```
    uv run --env-file .env -- upperroom runserver
    ```
