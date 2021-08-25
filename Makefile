lint:
	pylint tweetfinder

requirements-dev:
	pip install -q -r requirements/dev.txt

test:
	pytest

build-release:
	find . -name '.DS_Store' -type f -delete
	python setup.py sdist

release-test:
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*

release:
	twine upload dist/*
