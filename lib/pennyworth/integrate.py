#!/usr/bin/python3

import copy


def compare(first, second, handler):
    first = copy.copy(first)
    second = copy.copy(second)
    for name, config in first.items():
        second_config = None
        if name in second:
            second_config = second[name]
            del second[name]
        handler(name, config, second_config)

    first_config = None
    for name, config in second.items():
        handler(name, first_config, config)
