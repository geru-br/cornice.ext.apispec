# flake8: noqa
# -*- coding: utf-8 -*-
import sys, os
try:
    # import mozilla_sphinx_theme
    import pylons_sphinx_themes
except ImportError:
    print("please install the 'mozilla-sphinx-theme' distribution")

sys.path.insert(0, os.path.abspath("../.."))
extensions = ['sphinx.ext.autodoc']

templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'
project = u'Cornice APISpec'
copyright = u'2016-2017, Tomas Correa'

version = '0.3'
release = '0.3.0'

exclude_patterns = []

html_theme_path = [os.path.dirname(pylons_sphinx_themes.__file__)]

# html_theme = 'mozilla'

html_theme = 'pyramid'

html_theme_path = pylons_sphinx_themes.get_html_themes_path()


html_static_path = ['_static']
