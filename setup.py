import os
from setuptools import setup, find_packages
from aristotle_mdr import get_version

VERSION = get_version()

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='aristotle-metadata-registry',
    version=VERSION,
    packages=find_packages(),
    include_package_data=True,
    license='Aristotle-MDR Modified BSD Licence',
    description='Aristotle-MDR is an open-source metadata registry as laid out by the requirements of the IEC/ISO 11179:2013 specification.',
    long_description=README,
    url='https://github.com/aristotle-mdr/aristotle-metadata-registry',
    author='Samuel Spencer',
    author_email='sam@aristotlemetadata.com',
    classifiers=[
        'Development Status :: 3 - Alpha',

        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Healthcare Industry',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Science/Research',

        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    install_requires = [
        "Django>=1.8,<1.11,!=1.9.*",
        'six', # Setuptools > 36 doesn't install this by default
        'pytz',
        'pyyaml',
        'lesscpy',

        'django-model-utils>=2.3.1',
        'django-notifications-hq>=1.0',
        'django-braces',
        'docutils',

        #Search requirements
        'django-haystack>=2.6.0,<2.7.0',

        #Rich text editors
        'django-ckeditor>=5.3.0',
        'pillow',

        # Revision control
        "django-reversion>=2.0,<2.1",
        'django-reversion-compare>=0.7,<0.8',
        'diff-match-patch',

        # Fancy UI stuff
        'django-static-precompiler',
        'django-autocomplete-light>=3.0.0',
        'django-bootstrap3',
        'django-bootstrap3-datetimepicker-2<2.5.0',

        'django-formtools',

        # required for help, but thats required
        'django-autoslug',
        # for more 'real-time' notifications
        'channels',
        'django-haystack-channels',
        'asgi-redis',
        
        # This is only needed for Migration 0024 once this is squashed, remove this dependency
        'sqlparse',
        
        # Required for utils.cached_querysets
        'dill',

    ],

)
