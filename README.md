# heureka-opc
One Product and Category Test Assignement

## Running with Docker Compose

Please clone the repository and add the `.env` config file to the root of the project first.
The environment variable names are in `.env.example`. Values can be consulted with
the developer.

The app can be started by using docker-compose. Please run in the root directory of the
project:

`docker-compose up`

Three containers should be running after the command: db - database, heurekaopc - the main app, testday-api - the
API for matching offers.

Once the app is running, the offers are loaded in the background from kafka, and you can connect to the API.

Shutting down the app:

`docker-compose down`

## Usage

The results can be read with provided API. The API is documented with automatic interactive API
documentation (provided by Swagger UI): http://127.0.0.1/docs

If you change the port of the API in `compose.yaml`, then you need to use this port
for this Swagger UI documentation as well.

When working with API, please always use the "id" from the data returned by the API when you see that the
result has both "id" and "_id".

## Development Setup

It is recommended to use [venv](https://docs.python.org/3/tutorial/venv.html).

For example:

`python3 -m venv heureka-opc`

`source heureka-opc/bin/activate`

It is possible to install Python packages straight from `requirements.txt`.

`python -m pip install -r requirements.txt`

The project is using [pip-tools](https://github.com/jazzband/pip-tools).

For further development, please install it:

`python -m pip install pip-tools`

Then you can alternativelly install all dependencies with the command:

`pip-sync`

More details at [pip-tools](https://github.com/jazzband/pip-tools).

## Linting

The project uses [flake8](https://github.com/PyCQA/flake8) and  [bandit](https://github.com/PyCQA/bandit)
and curently it is intended to run the linting as part of pre-commit Git hook although the developer
can run the linting manually.

Formatting is done with [black](https://github.com/psf/black). [Integrating black with Pycharm](https://black.readthedocs.io/en/stable/integrations/editors.html#pycharm-intellij-idea) and
thus running it automatically with each save of a file brings most pleasure.

**Setupping Git hooks**

Developer can setup the linting on each commit with:

```
 $ pre-commit install
```

## Environment Setup

The `.env` file in the root directory of the project should contain the configuration of
the client that consumes records from a kafka cluster. More over there are configurations
of mongodb database and offer matching API.

In the file `compose.yaml`, you can change some behaviours. By default, I leave the mongodb
port exposed, so I can access the database outside of docker for debugging and data monitoring.
It can be hidden by deleting the `ports:` part for `db` service. The results retrieval API
runs on port 80. If you want to reach the API on different port, e.g., 8080, please change
the `ports:` value to `- '8080:80'` for the `heurekaopc` service.


## Running Tests

If you did the development setup, you can then execute automatic tests by executing
following command in the root directory of the project:

`pytest`
