# heureka-opc
One Product and Category Test Assignement

## Running by Docker

## Usage

## Development Setup

It is possible to install Python packages straight from `requirements.txt`.

`python -m pip install -r requirements.txt`

The project is using [pip-tools](https://github.com/jazzband/pip-tools).

For further development, please install it:

`(venv) $ python -m pip install pip-tools`

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

## Running Tests
