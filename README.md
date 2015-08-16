# bOTL.py
bOTL Object Transformation Language v3

This is a python implementation of bOTL v3

You can read the [bOTL specification] (https://medium.com/@emlynoregan/botl-object-transformation-language-35ed297c6671).

Usage:
Just grab the file bOTL.py and use it like this:

  import bOTL

  source = {"name": "Freddo"}
  transform = "#$.name"
  result = bOTL.transform(source, transform)

  # result: "Freddo" 

Also make sure you've installed or otherwise have available JSONPath RW by kennknowles:
[JSONPath RW](https://github.com/kennknowles/python-jsonpath-rw)

