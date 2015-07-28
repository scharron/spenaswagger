#!/usr/bin/env python

from setuptools import setup
from importlib import import_module
import re

packagename = "spenaswagger"


def pip(filename):
    RE_REQUIREMENT = re.compile('^\s*-r\s*(?P<filename>.*)$')
    RE_SCM = re.compile("^(git|svn|hg)\+.*$")
    requirements = []
    for line in open(filename):
        match = RE_REQUIREMENT.match(line)
        scm = RE_SCM.match(line)
        if match:
            requirements.extend(pip(match.group('filename')))
        elif not scm:
            requirements.append(line.strip())
        else:
            # Ignore SCMs for deps.
            pass
    return requirements


setup(
    # the package author
    author="Samuel Charron",
    # the package author's email
    author_email="samuel.charron@gmail.com",

    # the package name
    name=packagename,
    entry_points={
        'console_scripts': [
            packagename + ' = ' + packagename + '.' + packagename + ':main',
        ],
    },
    # Additional files to package
    package_data={'': ['version.txt', "templates/*"]},
    # Version number, from the import above
    version=import_module(packagename).__version__,
    # the package url
    url='http://github.com/scharron/%s' % packagename,
    # the package name
    packages=[packagename],
    # the package description
    description=open("README.rst").read().strip(),
    # recursive dependencies
    install_requires=pip("deps.txt"),
    # To avoid uploading right now
    classifiers=['Private :: Do Not Upload'],
)
