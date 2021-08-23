lint:
	pylint tweetfinder

requirements-dev:
	pip install -q -r requirements/dev.txt

test:
	pytest

evaluate-csv:
	python -m scripts.evaluate-from-csv

evaluate-files:
	python -m scripts.evaluate-from-files

build-release:
	find . -name '.DS_Store' -type f -delete
	python setup.py sdist

release-test:
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*

release:
	twine upload dist/*
