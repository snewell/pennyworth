#!/usr/bin/python3

import jenkinsapi.jenkins
import os

import pennyworth.config

_DEFAULT_PATH = os.path.join(os.path.expanduser("~"), ".pennyworth.d")


def get_hosts():
    return pennyworth.config.read_config(os.path.join(_DEFAULT_PATH,
                                                      "hosts.conf"))


class Host:
    def __init__(self, *args, **kwargs):
        self._host = jenkinsapi.jenkins.Jenkins(*args, **kwargs)

    def list_jobs(self):
        return self._host.get_jobs_list()


def make_host(host_config, folder=None):
    kwargs = {
        'baseurl': host_config.get('uri'),
        'username': host_config.get('username'),
        'password': host_config.get('password')
    }
    if host_config.get('verify_ssl', True) == 'false':
        kwargs['ssl_verify'] = False
    if folder:
        folders = folder.split('/')
        kwargs['baseurl'] += "/{}{}".format("job/", "/job/".join(folders))
    # print(kwargs)
    return Host(**kwargs)
