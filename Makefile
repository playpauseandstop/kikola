.PHONY: clean distclean

project=testproject
python=PYTHONPATH=. python

manage=$(python) $(project)/manage.py

clean:
	$(MAKE) -C $(project) clean
	$(python) setup.py clean
	find . -name '*.pyc' -delete

distclean:
	-rm -rf build/
	-rm -rf dist/
	-rm MANIFEST

test:
	$(manage) test {base,core,shortcuts,templatetags}
