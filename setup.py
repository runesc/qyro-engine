import json
import os
from setuptools import setup, find_packages
from os.path import relpath, join

def _load_package_json():
    with open('package.json', 'r', encoding='utf-8') as file:
        return json.loads(file.read())

def _get_package_data(pkg_dir, data_subdir):
    result = []
    for dirpath, _, filenames in os.walk(join(pkg_dir, data_subdir)):
        for filename in filenames:
            filepath = join(dirpath, filename)
            result.append(relpath(filepath, pkg_dir))
    return result

PACKAGE = _load_package_json()

setup(
    name=PACKAGE['name'],
    version=PACKAGE['version'],
    description=PACKAGE['description'],
    long_description=PACKAGE['long_description'],
    long_description_content_type='text/markdown',
    author=PACKAGE['author'],
    author_email=PACKAGE['author_email'],
    url=PACKAGE['homepage'],
    packages=find_packages(exclude=('tests', 'tests.*')),
    install_requires=['PyInstaller>=6.9.0', "pydantic>=2.11.7",
                      "questionary>=2.1.0", "rich>=14.1.0", "watchdog>=6.0.0", "astor>=0.8.1", "pillow>=11.3.0"],
    package_data={
        'qyro': _get_package_data('qyro', '_default_settings'),
        'qyro.cli_commands': (
            _get_package_data('qyro/cli_commands', 'boilerplate')
            + ['package.json']
        )
    },
    data_files=[
        ('qyro/cli_commands', ['package.json']),
    ],
    extras_require={
        'licensing': ['rsa>=3.4.2'],
        'sentry': ['sentry-sdk>=0.6.6'],
        'upload': ['boto3']
    },
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules'

        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    entry_points={
        'console_scripts': ['qyro=qyro.__main__:main', 'ppg=qyro.__main__:main']
    },
    license=PACKAGE['license'],
    keywords=PACKAGE['keywords'],
    platforms=['MacOS', 'Windows', 'Debian',
               'Fedora', 'CentOS', 'Arch', 'Raspbian'],
    test_suite='tests',
)