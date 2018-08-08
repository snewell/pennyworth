#!/usr/bin/python3

import os.path
import re

import pennyworth.config
import pennyworth.job_template


class ChunkCache:
    def __init__(self):
        self._cache = {}

    def get(self, key, fallback=None):
        return self._cache.get(key, fallback)

    def set(self, key, value):
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


class JobConfigs:
    def __init__(self, config):
        self._config = config

    def get_jobs(self):
        return self._config.sections()

    def get_job_chunks(self, job_name):
        if self._config.has_option(job_name, 'chunks'):
            return _make_chunk_iterator(self._config[job_name])
        elif self._config.has_option(job_name, 'template'):
            return _make_template_iterator(self._config[job_name])

    def get_job_subs(self, job_name):
        subs = []
        for option, value in self._config[job_name].items():
            match = _OPTION_PATTERN.match(option)
            if match:
                sub = re.compile("@@{}@@".format(option[match.end():].upper()))
                subs.append((sub, value))
        return subs


def make_configs(config_path):
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
    config = _build_config(chunks, cache)
    return _sub_config(config, subs)


def generate_configs():
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
