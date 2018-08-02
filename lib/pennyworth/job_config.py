#!/usr/bin/python3

import re

import pennyworth.config


class ChunkCache:
    def __init__(self):
        self._cache = {}

    def get(self, key, fallback=None):
        return self._cache.get(key, fallback)

    def set(self, key, value):
        self._cache[key] = value


_OPTION_PATTERN = re.compile(R"^sub\.")


class JobConfigs:
    def __init__(self, config):
        self._config = config

    def get_jobs(self):
        return self._config.sections()

    def get_job_chunks(self, job_name):
        job_chunks = self._config[job_name].get('chunks')
        return [chunk.strip() for chunk in job_chunks.split(',')]

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
