.PHONY: init
init:
	pip install -e ".[dev]"
	pip install tox tox-pyenv pre-commit
	pre-commit install
