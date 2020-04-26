import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname), encoding='UTF8').read()


setup(
    name = "jws",
    version = "0.1.3",
    author = "Brian J Brennan",
    author_email = "brianloveswords@gmail.com",
    description = ("JSON Web Signatures implementation in Python"),
    license = "MIT",
    keywords = "jws json web security signing",
    url = "http://github.com/brianloveswords/python-jws",
    packages=['jws'],
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
    ],
    test_suite = 'nose.collector',
)
