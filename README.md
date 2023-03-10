# Colored Cat

[![Build](https://github.com/helviojunior/pyccat/actions/workflows/build_and_publish.yml/badge.svg)](https://github.com/helviojunior/pyccat/actions/workflows/build_and_publish.yml)
[![Build](https://github.com/helviojunior/pyccat/actions/workflows/build_and_test.yml/badge.svg)](https://github.com/helviojunior/pyccat/actions/workflows/build_and_test.yml)
[![Downloads](https://pepy.tech/badge/pyccat/month)](https://pepy.tech/project/pyccat)
[![Supported Versions](https://img.shields.io/pypi/pyversions/pyccat.svg)](https://pypi.org/project/pyccat)
[![Contributors](https://img.shields.io/github/contributors/helviojunior/pyccat.svg)](https://github.com/helviojunior/pyccat/graphs/contributors)
[![PyPI version](https://img.shields.io/pypi/v/pyccat.svg)](https://pypi.org/project/pyccat/)
[![License: GPL-3.0](https://img.shields.io/pypi/l/pyccat.svg)](https://github.com/helviojunior/pyccat/blob/main/LICENSE)

CCat officially supports Python 3.8+.

## Main features

* [x] Read and highlight text and conde files

## Installation

```bash
pip3 install --upgrade pyccat
```

## Getting stats

***Read a file***
```bash
ccat /tmp/teste.json
```

![Sample 001](images/sample_001.jpg)

***Read a file without table***
```bash
ccat -nt /tmp/teste.json
```

![Sample 002](images/sample_002.jpg)

***Just highlight the file***
```bash
ccat -s /tmp/teste.json
```

![Sample 003](images/sample_003.jpg)
