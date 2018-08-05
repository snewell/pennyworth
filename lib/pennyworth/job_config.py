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
        def __init__(self, chunks):
            self._chunks = chunks
            self._iter = iter(chunks)

        def __iter__(self):
            return self

        def __next__(self):
            return next(self._iter)

    job_chunks = job_config.get('chunks')
    return _ChunkIterator([chunk.strip() for chunk in job_chunks.split(',')])


def _make_template_iterator(job_config):
    class _TemplateIterator:
        def __init__(self, template_config):
            template_chunks = template_config.get_config().get('chunks')
            chunks = [chunk.strip() for chunk in template_chunks.split(',')]
            print("chunks = {}".format(chunks))
            self._template_config = template_config
            self._iter = iter(chunks)

        def __iter__(self):
            return self

        def __next__(self):
            chunk_name = next(self._iter)
            return os.path.join(
                self._template_config.get_template_folder(), chunk_name)

    template_config = pennyworth.job_template.get_job_template(
        job_config['template'])
    return _TemplateIterator(template_config)


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
