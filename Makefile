.PHONY: clean distclean manage runserver shell test

python=PYTHONPATH=. python

# Read current version of Kikola
VERSION=`$(python) -c 'import kikola; print kikola.get_version()'`

clean:
	find . -name '*.pyc' -delete
	$(python) setup.py clean

distclean:
	-rm -rf build/
	-rm -rf dist/
	-rm MANIFEST

manage:
	$(MAKE) -C testproject manage

runserver:
	$(MAKE) -C testproject runserver

shell:
	$(MAKE) -C testproject shell

test:
	$(MAKE) -C testproject test

version:
	git tag -a $(VERSION) -f -m '$(VERSION) release'
	git push --tags origin master
	$(python) setup.py register sdist upload
