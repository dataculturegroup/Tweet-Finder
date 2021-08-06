lint.py:
	pylint tweetfinder

requirements-dev:
	pip install -q -r requirements/dev.txt
	python -m spacy download en_core_web_sm

test:
	pytest

evaluate:
	python -m scripts.evaluate

build-release:
	find . -name '.DS_Store' -type f -delete
	python setup.py sdist

release-test:
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*

release:
	twine upload dist/*
