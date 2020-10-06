# The Point Church Website #

This is a Django project for The Point Church's website.

## Development

To set up a development environment:

1. [Install poetry](https://python-poetry.org/docs/#installation)

2. Clone the `testing` repository:

    ```
    git clone -branch testing https://github.com/thepointchurch/thepoint.git
    cd thepoint
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
    export DB_ENGINE='django.db.backends.sqlite3'
    export DB_NAME='thepoint.sqlite3'
    export SECRET_KEY='12345678'
    export DJANGO_SETTINGS_MODULE=thepoint.settings
    ```

5. Start a test server:

    ```
    thepoint runserver
    ```
