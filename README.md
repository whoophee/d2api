# d2api

## Introduction
Python 3 wrapper and parser for interacting with Valve's Dota 2 WebAPI.

| Documentation |
| ------------- |
| [![Documentation](https://readthedocs.org/projects/d2api/badge/?version=latest)](https://readthedocs.org/projects/d2api/?badge=latest) |

This project is still growing, with additonal parsing, tests,  documentation and examples.

## Installation

### Install using pip (recommended)
Install from pip using:
```bash
$ pip install d2api
```

### Clone from github
Download the latest build and install using:
```bash
$ git clone https://github.com/whoophee/d2api/
$ cd d2api/
$ python setup.py install
```

## Getting Started

First of all, you need an API key from [Steam](https://steamcommunity.com/dev/apikey). Once that's done, you can initialize the wrapper in one of two ways.

#### Initialize using Environment Variable
Set the environment variable ``D2_API_KEY`` to the API key you just generated, and then initialize your wrapper using,
```python
api = d2api.APIWrapper()
```
#### Initialize inline
You can also initialize the wrapper inline using,
```python
# This takes priority over the environment variable
api = d2api.APIWrapper(api_key = 'your api key')
```

You can find further use cases and examples [here](https://d2api.readthedocs.io/en/latest/tutorial.html).

## Documentation

Documentation is available at [http://d2api.readthedocs.org/](http://d2api.readthedocs.org/)
