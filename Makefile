.PHONY: init
init:
	pip install -e ".[dev]"
	pip install --upgrade tox pre-commit scriv
	rm -rf .tox
	pre-commit install
