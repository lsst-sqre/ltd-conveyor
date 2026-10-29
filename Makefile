.PHONY: init
init:
	pip install -e ".[dev]"
	pip install --group docs
	pip install --upgrade tox pre-commit scriv
	rm -rf .tox
	pre-commit install
