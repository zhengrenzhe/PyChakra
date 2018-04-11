# -*- coding: utf-8 -*-

from setuptools import setup
from os import system
from os.path import abspath, dirname

ROOT = abspath(dirname(__file__))

# download Chakra binaries
system(ROOT + "/build.sh")

setup(
    name="PyChakra",
    packages=["PyChakra"],
    package_dir={"PyChakra": "PyChakra"},
    version="0.0.2",
    description="Python binding to Microsoft Chakra Javascript engine",
    long_description=open('README.md').read(),
    author="zhengrenzhe",
    author_email="zhengrenzhe.niujie@gmail.com",
    include_package_data=True,
    url="https://github.com/zhengrenzhe/PyChakra",
    keywords=["JavaScript", "Chakra", "engine", "binding"],
    license="MIT",
    classifiers=(
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
    )
)
