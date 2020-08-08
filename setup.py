import os
from pathlib import Path
from setuptools import find_packages, setup

import thepoint

with (Path(__file__) / 'README.md').open() as readme:
    README = readme.read()

os.chdir(Path(__file__).resolve(strict=True).parent)

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
        'Django>=3.1',
        'django-storages',
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 3.1',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
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
