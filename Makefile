.PHONY: init
init:
	pip install -e ".[dev]"
	pip install --upgrade tox tox-pyenv pre-commit
	pre-commit install
