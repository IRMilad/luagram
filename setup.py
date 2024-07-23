#!/usr/bin/env python3

import os
import re
from setuptools import setup


root = os.path.abspath(os.path.dirname(__file__))


def get_version():
    with open(os.path.join(root, 'src/luagram/luagram.py')) as file:
        for line in file:
            match = re.match('__version__ = \'(.*)\'', line)
            if match:
                return match.group(1)
    raise SystemExit('Could not find version string')


with open('README.md', encoding='utf-8') as file:
    long_description = file.read()


keywords = [
    'luagram',
    'lua-mtproto',
    'luagram-client',
    'luagram-mtproto',
    'telegram-client',
    'telegram-mtproto'
]
requirements = ['lupa>=2.2']


setup(
    name='luagram',
    version=get_version(),
    packages=['src', 'src/luagram', 'src/luagram/gadget'],
    package_data={},
    url='https://github.com/irmilad/luagram',
    license='MIT',
    author='Milad Heidary',
    description='lua telegram client',
    install_requires=requirements,
    python_requires='>=3',
    entry_points={'console_scripts': ['luagram=src.__main__:main']},
    zip_safe=False,
    keywords=keywords,
    long_description=long_description,
    long_description_content_type='text/markdown'
)