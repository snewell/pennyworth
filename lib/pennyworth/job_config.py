#!/usr/bin/python3

import pennyworth.config


class ChunkCache:
    def __init__(self):
        self._cache = {}

    def get(self, key, fallback=None):
        return self._cache.get(key, fallback)

    def set(self, key, value):
        self._cache[key] = value


class JobConfigs:
    def __init__(self, config):
        self._config = config

    def get_jobs(self):
        return self._config.sections()

    def get_job_chunks(self, job_name):
        job_chunks = self._config[job_name].get('chunks')
        return [chunk.strip() for chunk in job_chunks.split(',')]


def make_configs(config_path):
    job_configs = pennyworth.config.read_config(config_path)
    return JobConfigs(job_configs)


def build_config(chunks, cache):
    config = ""
    for chunk in chunks:
        chunk_data = cache.get(chunk)
        if not chunk_data:
            with open(chunk) as chunk_file:
                chunk_data = chunk_file.read()
            cache.set(chunk, chunk_data)
        config += chunk_data
    return config
