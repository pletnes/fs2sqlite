.PHONY: all

all:
	isort --profile=black fs2sqlite.py
	black fs2sqlite.py
	mypy fs2sqlite.py
