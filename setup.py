from distutils.core import setup
from setuptools import find_packages

setup(
    name='calypso',
    version='1.0.0',
    packages=find_packages(),
    scripts=[],
    url='',
    license='',
    author=['arueda', 'priesgo'],
    author_email=['antonio-rueda-martin@genomicsengland.co.uk', 'pablo.riesgo-ferreiro@genomicsengland.co.uk'],
    description='',
    # 'django-celery-results', 'django-filter',
    install_requires=[
        'amqp==2.2.2',
        'billiard==3.5.0.3',
        'celery==4.1.0',
        'coreapi==2.3.3',
        'Django==1.11.5',
        'django-celery-results==1.0.1',
        'django-filter==1.1.0',
        'djangorestframework==3.7.7',
        'Markdown==2.6.10',
        'Pygments==2.2.0',
        'pymongo==3.5.1',
        'mock==2.0.0'
    ]
)
