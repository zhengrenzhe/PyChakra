# -*- coding: utf-8 -*-

from os import system
from sys import platform
from setuptools import setup
from os.path import abspath, dirname

ROOT = abspath(dirname(__file__))

# download Chakra binaries
if platform == "win32":
    system("powershell.exe -executionpolicy unrestricted -command .\\build.ps1")  # noqa:E501
elif platform == "darwin" or platform.startswith("linux"):
    system(ROOT + "/build.sh")
else:
    raise RuntimeError("not support your platform: %s", platform)

setup(
    name="PyChakra",
    packages=["PyChakra"],
    package_dir={"PyChakra": "PyChakra"},
    version="0.0.3",
    description="Python binding to Microsoft Chakra Javascript engine",
    long_description=open('README.md').read(),
    author="zhengrenzhe",
    author_email="zhengrenzhe.niujie@gmail.com",
    include_package_data=True,
    url="https://github.com/zhengrenzhe/PyChakra",
    keywords=["Chakra", "JavaScript", "js engine", "binding"],
    license="MIT",
    python_requires=">=2.6, !=3.0.*, !=3.1.*, !=3.2.*",
    classifiers=(
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    )
)
