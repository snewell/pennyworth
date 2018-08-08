#!/usr/bin/python3

"""Functionality related to template configurations."""

import os.path

import pennyworth.config
import pennyworth.paths


class JobTemplate:
    """
    A template to create Jobs.
    """

    def __init__(self, template_folder, template_config):
        self._folder = template_folder
        self._config = template_config

    def get_template_folder(self):
        """
        Retrieve the folder containing the template definition.

        Returns:
        The folder (as a String) containing the template definition.
        """
        return self._folder

    def get_config(self):
        """
        Retrieve the template's configuration.

        Returns:
        The template's configuration.  This is an internal configparser object
        that functions a lot like a dictionary.
        """
        return self._config


def get_job_template(template_name):
    """
    Retrieve a JobTemplate for a specific template.

    Arguments:
    template_name - The template to load.

    Returns:
    A JobTemplate for template_name.
    """
    path_parts = template_name.split('/')
    template_folder = os.path.join(
        pennyworth.paths.get_config_root(), *path_parts[:-1])
    expected_path = os.path.join(template_folder, 'templates.conf')
    template_config = pennyworth.config.read_config(expected_path)
    return JobTemplate(template_folder, template_config[path_parts[-1]])
