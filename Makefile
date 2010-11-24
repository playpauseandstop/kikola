.PHONY: clean distclean manage runserver shell test

project=testproject
python=PYTHONPATH=. python

manage=$(python) $(project)/manage.py

# Settings for runserver target
IP?=0.0.0.0
PORT?=8197

# Settings for runserver and shell targets
DJANGO_RUNSERVER?=runserver_plus
DJANGO_SHELL?=shell_plus

# Settings for test target
TEST?={base,core,db,shortcuts,templatetags,utils}
TEST_ARGS?=--settings=$(project).settings_testing

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
	$(manage) $(COMMAND)

runserver:
	$(manage) $(DJANGO_RUNSERVER) $(IP):$(PORT)

shell:
	$(manage) $(DJANGO_SHELL)

test:
	$(manage) test $(TEST_ARGS) $(TEST)

version:
	git tag -a $(VERSION) -f -m '$(VERSION) release'
	git push --tags origin master
	$(python) setup.py register sdist upload
