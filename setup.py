import os
from setuptools import find_packages, setup

import thepoint

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='thepoint',
    version=thepoint.__version__,
    license=open('LICENSE').read(),
    description='''A Django project for The Point Church's website.''',
    long_description=README,
    packages=find_packages(),
    include_package_data=True,
    url='https://www.thepoint.org.au/',
    author='Craig Holyoak',
    author_email='craig@helmsdeep.org',
    install_requires=[
        'Django>=3.0',
        'django-storages',
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 3.0',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    scripts=[
        'bin/thepoint-backup',
        'bin/thepoint-manage',
        'bin/thepoint-restore',
        'bin/thepoint-sendrosteremails',
    ],
)
