#!/usr/bin/python3

"""
Functionality related to Jenkins host manipulation.
"""

import os
import jenkinsapi.jenkins

import pennyworth.config

_DEFAULT_PATH = os.path.join(os.path.expanduser("~"), ".pennyworth.d")


def get_hosts():
    """
    Get the list of available hosts.  Note that for the sake of this function,
    available means definied in a configuration file, not that the host is
    actually online or reachable with the specified credentials.

    Returns a list of hosts defined in a hosts.conf file.
    """
    return pennyworth.config.read_config(os.path.join(_DEFAULT_PATH,
                                                      "hosts.conf"))


class Host:
    """A Jenkins host to operate on."""

    def __init__(self, *args, **kwargs):
        self._host = jenkinsapi.jenkins.Jenkins(*args, **kwargs)

    def list_jobs(self):
        """
        Retrieve jobs configured on the Host.

        Returns a list of tuples containing 1) the job name and 2) a
        jenkinsapi.job.Job instance
        """
        return self._host.get_jobs()

    def change_job(self, name, xml):
        job = self._host.get_job(name)
        return job.update_config(xml)

    def create_job(self, name, xml):
        return self._host.create_job(name, xml)

    def erase_job(self, name):
        return self._host.delete_job(name)


def make_host(host_config, folder=None):
    """
    Make a Host object based on a configuration an optional folder.

    Arguments
    host_config - A host configuration from a hosts.conf.
    folder - A folder in the Jenkins instance to operate in.
    """
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
