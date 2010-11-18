.PHONY: clean distclean fullsyncdb manage runserver shell syncdb test

# Basic settings
env?=env
project?=testproject
python?=python -Wignore::DeprecationWarning

manage=PYTHONPATH=. $(python) manage.py

# Settings for runserver command
IP?=0.0.0.0
PORT?=8195

# Settings for runserver and shell commands
DJANGO_RUNSERVER?=runserver
DJANGO_SHELL?=shell

clean:
	find . -name '*.pyc' -delete

distclean: clean
	-rm $(project).db
	-rm -rf $(env)

fullsyncdb:
	-rm $(project).db
	$(MAKE) syncdb

manage:
	$(manage) $(COMMAND)

runserver:
	$(manage) $(DJANGO_RUNSERVER) $(IP):$(PORT)

shell:
	$(manage) $(DJANGO_SHELL)

syncdb:
	$(manage) syncdb --noinput

test:
	$(manage) test
