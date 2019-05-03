import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='thepoint',
    version='2.0.1',
    license=open('LICENSE').read(),
    description='''A Django project for The Point Church's website.''',
    long_description=README,
    packages=find_packages(),
    include_package_data=True,
    url='https://www.thepoint.org.au/',
    author='Craig Holyoak',
    author_email='craig@helmsdeep.org',
    install_requires=[
        'Django>=2.1',
        'django-storages',
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 2.2',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
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
