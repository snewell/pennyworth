#!/usr/bin/python3

"""
Code to support integration between different source of job configuration.

The most common scenario for different sources is working with a jobs on
Jenkins host compared to generated configurations, but the code here should
remain generic.
"""

import copy


def compare(first, second, handler):
    """
    Compare two sources of jobs, calling a handler function based on the
    results.

    handler will be called under the following conditions:
      - a job's configuration differs
      - a job only exists in one set

    Arguments:
    first - The first source of job configurations.
    second - The second source of job configurations.
    handler - A function to call based on changes.  handler should take three
              arguments:
                1) the name of the job being considered
                2) the configuration in the first set (None if it doesn't
                   exist)
                3) the configuration in the second set (None if it doesn't
                   exist)
    """
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
