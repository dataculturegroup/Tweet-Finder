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
	pandoc README.md --from markdown --to rst -s -o docs-sphinx/source/README.rst
	cat docs-sphinx/source/README.rst docs-sphinx/source/footer.rst > docs-sphinx/source/index.rst
	rm docs-sphinx/source/README.rst
	rm README.rst
	sphinx-build -b html docs-sphinx/source/ docs-sphinx/build/html
	cp -r docs-sphinx/build/html/* docs
