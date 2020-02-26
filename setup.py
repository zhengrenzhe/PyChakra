# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name="PyChakra",
    version="2.3.0",
    packages=["PyChakra"],
    package_dir={"PyChakra": "PyChakra"},
    description="Python binding to Microsoft Chakra JavaScript engine",
    long_description=open("README.rst").read(),
    author="zhengrenzhe",
    author_email="zhengrenzhe.niujie@gmail.com",
    url="https://github.com/zhengrenzhe/PyChakra",
    keywords="Chakra ChakraCore V8 JavaScript js-engine binding",
    license="MIT",
    python_requires=">2.6, !=3.0.*, !=3.1.*, !=3.2.*",
    include_package_data=True,
    package_data={
        "libs": [
            "PyChakra/libs/linux/libChakraCore.so",
            "PyChakra/libs/osx/libChakraCore.dylib",
            "PyChakra/libs/windows/x64/ChakraCore.dll",
            "PyChakra/libs/windows/x86/ChakraCore.dll",
        ]
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ]
)
