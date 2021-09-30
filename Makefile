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

sphinx-docs:
	pandoc README.md --from markdown --to rst -s -o README.rst
	pandoc README.md --from markdown --to rst -s -o docs/source/README.rst
	cat docs/source/README.rst docs/source/footer.rst > docs/source/index.rst
	rm docs/source/README.rst
	rm README.rst
	sphinx-build -b html docs/source/ docs/build/html
