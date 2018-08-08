#!/usr/bin/python3

"""Types and functions to support job configuration."""

import os.path
import re

import pennyworth.config
import pennyworth.job_template


class ChunkCache:
    """
    A class to cache configuration chunks.

    Since pennyworth stitches together different files to form complete
    configurations, it's likely that many jobs will share many of the same
    chunks (e.g., the beginning and end of job configuration).  This class
    keeps a cache of file contents to avoid opening and closing the same file
    multiple times.
    """

    def __init__(self):
        self._cache = {}

    def get(self, key, fallback=None):
        """
        Get file contents from the cache.

        Arguments:
        key - The filename to look up.
        fallback - The return value if key isn't cached.

        Return:
        If key is cached, then the contents of its file.  If it's not in the
        cache, then fallback.
        """
        return self._cache.get(key, fallback)

    def set(self, key, value):
        """
        Set cache contents.

        Arguments:
        key - The filename being cached.
        value - The conents of key.
        """
        self._cache[key] = value


_OPTION_PATTERN = re.compile(R"^sub\.")


def _make_chunk_iterator(job_config):
    class _ChunkIterator:
        # pylint: disable=too-few-public-methods
        def __init__(self, chunks):
            self._chunks = chunks
            self._iter = iter(chunks)

        def __iter__(self):
            return self

        def __next__(self):
            return next(self._iter)

    job_chunks = job_config.get('chunks')
    return _ChunkIterator([chunk.strip() for chunk in job_chunks.split(',')])


class _TemplateIterator:
    # pylint: disable=too-few-public-methods
    def __init__(self, template_config, job_config):
        template_chunks = template_config.get_config().get('chunks')
        chunks = [chunk.strip() for chunk in template_chunks.split(',')]
        self._job_config = job_config
        self._template_config = template_config
        self._template_iter = iter(chunks)
        self._local_iter = None

    def __iter__(self):
        return self

    def _next_chunk(self):
        if self._local_iter:
            try:
                return next(self._local_iter)
            except StopIteration:
                self._local_iter = None
        return None

    def __next__(self):
        next_value = self._next_chunk()
        if not next_value:
            chunk_name = next(self._template_iter)
            if chunk_name in self._job_config:
                local_chunks = [
                    chunk.strip() for chunk in
                    self._job_config[chunk_name].split(',')]
                self._local_iter = iter(local_chunks)
                return self._next_chunk()
            return os.path.join(
                self._template_config.get_template_folder(), chunk_name)
        return next_value


def _make_template_iterator(job_config):
    template_config = pennyworth.job_template.get_job_template(
        job_config['template'])
    return _TemplateIterator(template_config, job_config)


_BUILD_METHODS = {
    'chunks': _make_chunk_iterator,
    'template': _make_template_iterator
}


class JobConfigs:
    """A class to work with job configuration"""

    def __init__(self, config):
        self._config = config

    def get_jobs(self):
        """Retrieve a lsit of available jobs."""
        return self._config.sections()

    def get_job_chunks(self, job_name):
        """
        Retrive an iterator that provides the chunks making up a job.

        Arguments:
        job_name - The name of the job to generate.
        """
        enabled_methods = []
        for option in self._config.options(job_name):
            if option in _BUILD_METHODS:
                enabled_methods.append(option)

        if len(enabled_methods) == 1:
            return _BUILD_METHODS[enabled_methods[0]](self._config[job_name])
        elif not enabled_methods:
            raise Exception(
                "{} doesn't specify a build method".format(job_name))
        raise Exception(
            "{} specifies multiple build methods ({})".format(
                job_name, enabled_methods))

    def get_job_subs(self, job_name):
        """
        Retrieve a list of string substitions for a job.

        Arguments:
        job_name - The job to generate substitions for.

        Return:
        A list of tuples, where the first element is a compiled-regular
        expression and the second element is the value to substite.
        """
        subs = []
        for option, value in self._config[job_name].items():
            match = _OPTION_PATTERN.match(option)
            if match:
                sub = re.compile("@@{}@@".format(option[match.end():].upper()))
                subs.append((sub, value))
        return subs


def make_configs(config_path):
    """
    Create a JobConfigs instance based on a configuration file.

    Arguments:
    config_path - Filesystem path to a job configuration file.

    Returns:
    A JobConfigs instance based on config_path.
    """
    job_configs = pennyworth.config.read_config(config_path)
    return JobConfigs(job_configs)


def _build_config(chunks, cache):
    config = ""
    for chunk in chunks:
        chunk_data = cache.get(chunk)
        if not chunk_data:
            with open(chunk) as chunk_file:
                chunk_data = chunk_file.read()
            cache.set(chunk, chunk_data)
        config += chunk_data
    return config


def _sub_config(config, subs):
    for compiled_re, value in subs:
        config = compiled_re.sub(value, config)
    return config


def build_config(chunks, cache, subs):
    """
    Build a job configuration.

    Arguments:
    chunks - An iterator to configuration chunks.  This should probably be
             something returned from JobConfigs.get_job_chunks.
    cache - A ChunkCache object.
    subs - Substitution patterns to use.  This should be something returned
           from JobConfigs.get_job_subs.

    Returns:
    An XML string of the generated job.
    """
    config = _build_config(chunks, cache)
    return _sub_config(config, subs)


def generate_configs():
    """
    Create all configurations specified in a jobs.conf file.

    Returns:
    A dictionary of job configurations.  The keys will be job names, and the
    values of each key will be XML configurations.
    """
    job_config = make_configs('jobs.conf')
    available_jobs = job_config.get_jobs()
    chunk_cache = ChunkCache()
    jobs = {}
    for job in available_jobs:
        config = build_config(
            job_config.get_job_chunks(job), chunk_cache,
            job_config.get_job_subs(job))
        jobs[job] = config
    return jobs
