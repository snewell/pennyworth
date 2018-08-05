#!/usr/bin/python3

import os.path

_DEFAULT_PATH = os.path.join(os.path.expanduser("~"), ".pennyworth.d")


def get_config_root():
    return _DEFAULT_PATH
