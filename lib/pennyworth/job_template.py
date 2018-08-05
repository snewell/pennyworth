#!/usr/bin/python3

import os.path

import pennyworth.config
import pennyworth.paths


class JobTemplate:
    def __init__(self, template_folder, template_config):
        self._folder = template_folder
        self._config = template_config

    def get_template_folder(self):
        return self._folder

    def get_config(self):
        return self._config


def get_job_template(template_name):
    path_parts = template_name.split('/')
    template_folder = os.path.join(
        pennyworth.paths.get_config_root(), *path_parts[:-1])
    expected_path = os.path.join(template_folder, 'templates.conf')
    template_config = pennyworth.config.read_config(expected_path)
    return JobTemplate(template_folder, template_config[path_parts[-1]])
