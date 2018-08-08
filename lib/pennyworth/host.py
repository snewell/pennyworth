#!/usr/bin/python3

"""
Functionality related to Jenkins host manipulation.
"""

import os
import re
import jenkinsapi.jenkins

import pennyworth.config
import pennyworth.paths


def get_hosts():
    """
    Get the list of available hosts.  Note that for the sake of this function,
    available means definied in a configuration file, not that the host is
    actually online or reachable with the specified credentials.

    Returns a list of hosts defined in a hosts.conf file.
    """
    return pennyworth.config.read_config(
        os.path.join(pennyworth.paths.get_config_root(), "hosts.conf"))


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
        """
        Change a job's configuration on a host.

        Arguments:
        name - The name of the job.
        xml - The xml configuration that should be applied.
        """
        job = self._host.get_job(name)
        return job.update_config(xml)

    def create_job(self, name, xml):
        """
        Create a new job on the host.

        Arguments:
        name - The name of the new job.
        xml - The configuration of the new job.
        """
        return self._host.create_job(name, xml)

    def erase_job(self, name):
        """
        Remove a job from the host.

        Arguments:
        name - The name of the job to remove.
        """
        return self._host.delete_job(name)


_DUPLICATE_END_SLASH_REGEX = re.compile(R"\/\/+$")


def _strip_trailing_slashes(uri):
    # If the uri has trailing slashes, something in the jenkinsapi library gets
    # confused.  This makes sure there aren't any slashes at the end of the
    # Jenkins URI.
    uri = _DUPLICATE_END_SLASH_REGEX.sub('/', uri)
    if uri[-1] == '/':
        return uri[:-1]
    return uri


_DUPLICATE_SLASH_REGEX = re.compile(R"\/\/+")


def _strip_bad_folder_slashes(folder):
    # same idea with slashes here
    folder = _DUPLICATE_SLASH_REGEX.sub('/', folder)
    first = 0
    if folder[0] == '/':
        first = 1
    if folder[-1] == '/':
        return folder[first:-1]
    return folder[first:]


def make_host(host_config, folder=None):
    """
    Make a Host object based on a configuration an optional folder.

    Arguments
    host_config - A host configuration from a hosts.conf.
    folder - A folder in the Jenkins instance to operate in.
    """
    kwargs = {
        'baseurl': _strip_trailing_slashes(host_config.get('uri')),
        'username': host_config.get('username'),
        'password': host_config.get('password')
    }
    if host_config.get('verify_ssl', True) == 'false':
        kwargs['ssl_verify'] = False
    if folder:
        folders = _strip_bad_folder_slashes(folder).split('/')
        kwargs['baseurl'] += "/{}{}".format("job/", "/job/".join(folders))
    return Host(**kwargs)


def get_host_configs(host):
    """
    Retrieve all jobs and their configurations from a host.

    Arguments:
    host - The Host to operate on.

    Returns:
    A dictionary of job configurations.  Each key will be a job name and the
    value will be the job's configuration as an XML string.
    """
    job_configs = {}
    for name, job in host.list_jobs():
        job_configs[name] = job.get_config()
    return job_configs
