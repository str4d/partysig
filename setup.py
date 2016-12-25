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
    download_url='https://github.com/str4d/partysig/tarball/%s'%versioneer.get_version(),
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
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
        'pyblake2',
        'pynacl',
    ],
    packages=[
        'partysig',
    ],
    entry_points={
        'console_scripts':
        [
            'partysig = partysig.cli:partysig',
        ]
    },
    cmdclass=versioneer.get_cmdclass(),
)
