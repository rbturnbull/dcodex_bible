from setuptools import setup

requirements = [
    'Django>3',
    'django-polymorphic',
    'numpy',
    'pandas>=1.0.5',
    'matplotlib',
    'requests',
    'lxml',
    'django-imagedeck @ git+https://gitlab.unimelb.edu.au/rturnbull/django-imagedeck.git#egg=django-imagedeck',
]

setup(
    install_requires=requirements,
)


