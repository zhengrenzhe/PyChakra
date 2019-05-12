PyChakra
========

|Build Status|

PyChakra is a Python binding to `Microsoft Chakra`_\ (v1.11.8)
Javascript engine. PyChakra will be downloading pre-compiled Chakra
binaries when install, so the process is fast and easy.

Chakra is a modern JavaScript engine for Microsoft Edge, it support 96%
ES6 feature, Complete info see
https://kangax.github.io/compat-table/es6/

Installation
------------

::

   pip install PyChakra

Usage
-----

.. code:: python

   from PyChakra import Runtime

   # create runtime instance
   runtime = Runtime()

   # eval JavaScript code
   runtime.eval("(() => 2)();") # (True, '2')
   runtime.eval("(() => a)();") # (False, "'a' is not defined")

   # set or get variable
   runtime.set_variable("foo", "'bar'") # True
   runtime.get_variable("foo") # bar

API
---

``eval(js_string)``
~~~~~~~~~~~~~~~~~~~

Eval JavaScript code string.

Parameters:

-  ``js_string: str``: JavaScript code string

Returns: ``(is_successful: bool, result: string|number)``

-  ``is_successfully``: indicates whether JavaScript is running
   successfully.
-  ``result``:

   -  if s is True, result is the JavaScript running return value.
   -  if is_successfully is False and result is string, result is the
      JavaScript running exception.
   -  if is_successfully is False and result is number, result is the
      chakra internal error code. see(\ `github`_)

``set_variable(variable_name: str, variable_value: any)``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Set variable in global scope.

Parameters:

-  ``variable_name: str``: JavaScript variable name.
-  ``variable_value: str``: JavaScript variable value in Python str.

Returns: same as eval

``get_variable(variable_name: str)``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Get variable in global scope.

Parameters:

-  ``variable_name: str``: JavaScript variable name.

Returns: ``variable_value: str`` - if returns value is None, it
indicates there is no ``variable_name`` in the global scope.

Supports
--------

-  Python2 >= 2.7
-  Python3 >= 3.4

Platform
--------

-  macOS x64
-  Linux x64
-  Windows x86/x64 (tested on Windows 10 x64, Python 3.7)

.. _Microsoft Chakra: https://github.com/Microsoft/ChakraCore
.. _github: https://github.com/Microsoft/ChakraCore/wiki/JsErrorCode

.. |Build Status| image:: https://travis-ci.org/zhengrenzhe/PyChakra.svg?branch=master
   :target: https://travis-ci.org/zhengrenzhe/PyChakra