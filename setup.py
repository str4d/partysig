# Copyright (c) Jack Grigg
# See LICENSE for details.

from setuptools import setup
import versioneer


with open('README.rst', 'rb') as infile:
    long_description = infile.read()

setup(
    name='partysig',
    version=versioneer.get_version(),
    description='Create and verify distributed multi-party signatures',
    long_description=long_description,
    author='Jack Grigg',
    author_email='str4d@i2pmail.org',
    url='https://github.com/str4d/partysig',
    classifiers=[
        'Development Status :: 1 - Planning',
        'Framework :: Twisted',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Topic :: Security',
    ],
    license='MIT',

    install_requires=[
        'magic-wormhole',
    ],
    packages=[
        'partysig',
    ],
    cmdclass=versioneer.get_cmdclass(),
)
