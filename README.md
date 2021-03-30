![Release](https://github.com/thepointchurch/upperroom/workflows/Release/badge.svg)
![Docker Image](https://github.com/thepointchurch/upperroom/workflows/Docker%20Image/badge.svg)

# Upper Room #

Upper Room is a framework for church websites.

## Development

To set up a development environment:

1. [Install poetry](https://python-poetry.org/docs/#installation)

2. Clone the `testing` repository:

    ```
    git clone -branch testing https://github.com/thepointchurch/upperroom.git
    cd upperroom
    ```

3. Set up the poetry environment:

    ```
    poetry install -E aws -E cache -E pgsql -E google
    poetry run pre-commit install
    poetry shell
    ```

4. Export config variables:

    ```
    export DEBUG='True'
    export DATABASE_URL='sqlite:///upperroom.sqlite3'
    export SECRET_KEY='12345678'
    export DJANGO_SETTINGS_MODULE=upperroom.settings
    ```

    or place them in a an environment file at `upperroom/.env`:

    ```
    cat >upperroom/.env <<DEV_ENV
    DEBUG='True'
    DATABASE_URL='sqlite:///upperroom.sqlite3'
    SECRET_KEY='12345678'
    DJANGO_SETTINGS_MODULE=upperroom.settings
    DEV_ENV
    ```

5. Start a test server:

    ```
    upperroom runserver
    ```
