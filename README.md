# PyChakra

[![Build Status](https://travis-ci.org/zhengrenzhe/PyChakra.svg?branch=master)](https://travis-ci.org/zhengrenzhe/PyChakra)

PyChakra is a Python binding to [Microsoft Chakra](https://github.com/Microsoft/ChakraCore)(v1.8.3) Javascript engine.
PyChakra will be downloading pre-compiled Chakra binaries when install, so the process is fast and easy.

Chakra is a modern JavaScript engine for Microsoft Edge, it support 96% ES6 feature, Complete info see [https://kangax.github.io/compat-table/es6/](https://kangax.github.io/compat-table/es6/)


## Installation

```
pip install git+https://github.com/zhengrenzhe/PyChakra.git -v
```

or manual

```
git clone https://github.com/zhengrenzhe/PyChakra.git
cd PyChakra
python setup.py install
```


## Usage

```python
from PyChakra import ChakraHandle

runtime = ChakraHandle()

runtime.eval_js("(()=>2)()") # (True, '2')
runtime.eval_js("(()=>a)()") # (False, "'a' is not defined")
runtime.eval_js("/Users/test/test.js") # (bool, result)
```


## API

### eval_js(script, source="")

Eval javascript string

Parameters:

 - script(str): javascript code string
 - source(str?): code path (optional)

Returns: (bool, result)

 - bool: indicates whether javascript is running successfully.
 - result:
   * if bool is True, result is the javascript running return value.
   * if bool is False and result is string, result is the javascript running exception.
   * if bool is False and result is number, result is the chakra internal error code. see([github](https://github.com/Microsoft/ChakraCore/wiki/JsErrorCode))

### eval_js_file(file_path)

Eval javascript from local file

Parameters:

 - script(path): javascript file absolute path

Returns: same as eval_js



## Supports

- Python >=2.6
- Python !=3.0.\*, !=3.1.\*, !=3.2.\*


## Platform
- macOS
- Linux
- Windows (tested on Windows 10 x64, Python 3.7)
