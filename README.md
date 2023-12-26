# dcodex bible

![pipline](https://github.com/rbturnbull/dcodex_bible/actions/workflows/pipeline.yml/badge.svg)
[<img src="https://img.shields.io/badge/code%20style-black-000000.svg">](<https://github.com/psf/black>)
[![slack](https://img.shields.io/badge/dcodex-Join%20on%20Slack-green?style=flat&logo=slack)](https://join.slack.com/t/dcodex/shared_invite/zt-y2jpxumc-lDGGr3ZjndVqYLoyfCh1gA)

An extension for dcodex to use biblical manuscripts.

## Installation

For a brand new dcodex site, it is easiest to install using [dcodex-cookiecutter](https://github.com/rbturnbull/dcodex-cookiecutter).

To install dcodex-bible as a plugin in a dcodex site already set up. Install with pip:
```
pip install -e https://github.com/rbturnbull/dcodex_bible.git#egg=dcodex_bible
```

Then add to your installed apps:
```
INSTALLED_APPS += [
    "dcodex_bible",
]
```

Then add the urls to your main urls.py:
```
urlpatterns += [
    path('dcodex_bible/', include('dcodex_bible.urls')),    
]
```

## Installing Bible Verses

To use the standard versification system of the Old and New Testaments, run this command:
```
python manage.py import-bible-verses
```

## Installing Reference Bibles

If you want to install a reference Bible text, you can use one (or more) of the following commands:
```
python manage.py import-world-english-bible
python manage.py import-sblgnt
python manage.py import-robinsonpierpont
python manage.py import-textusreceptus
python manage.py import-tisch
python manage.py import-westcotthort
python manage.py import-smithvandyck
python manage.py import-smithvandyck-nt
python manage.py import-swete
```

## Sources

World English Bible: https://github.com/TehShrike/world-english-bible
