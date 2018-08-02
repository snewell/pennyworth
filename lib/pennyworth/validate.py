#!/usr/bin/python3

import difflib

import pennyworth.command
import pennyworth.host
import pennyworth.job_config


def _get_jenkins_configs(host):
    job_configs = {}
    for name, job in sorted(host.list_jobs()):
        job_configs[name] = job.get_config()
    return job_configs


def _get_generated_configs():
    job_config = pennyworth.job_config.make_configs('jobs.conf')
    available_jobs = job_config.get_jobs()
    chunk_cache = pennyworth.job_config.ChunkCache()
    jobs = {}
    for job in available_jobs:
        config = pennyworth.job_config.build_config(
            job_config.get_job_chunks(job), chunk_cache,
            job_config.get_job_subs(job))
        jobs[job] = config
    return jobs


def _print_diff(name, jenkins_lines, generated_lines):
    diffs = difflib.unified_diff(jenkins_lines, generated_lines,
                                 "jenkins/{}".format(name),
                                 "generated/{}".format(name))
    for _ in range(3):
        print(next(diffs), end='')
    for diff in diffs:
        print(diff)


def _print_diffs(jenkins_configs, generated_configs):
    for name, config in jenkins_configs.items():
        jenkins_lines = config.split('\n')
        generated_lines = []
        if name in generated_configs:
            generated_lines = generated_configs[name].split('\n')
            del generated_configs[name]
        _print_diff(name, jenkins_lines, generated_lines)

    jenkins_lines = []
    for name, config in generated_configs.items():
        generated_lines = config.split('\n')
        _print_diff(name, jenkins_lines, generated_lines)


class ValidateCommand(pennyworth.command.HostCommand):
    def __init__(self):
        super().__init__(prog="pennyworth validate",
                         description="Compare generated job configurations "
                                     "with what's actually in Jenkins")

    def process(self, parsed_args):
        host = self.make_host(parsed_args)
        jenkins_configs = _get_jenkins_configs(host)
        generated_configs = _get_generated_configs()
        _print_diffs(jenkins_configs, generated_configs)


def main(args=None):
    # pylint: disable=missing-docstring
    validate = ValidateCommand()
    pennyworth.command.execute_command(validate, args)


_VALIDATE_COMMAND = (
    main,
    "Validate configurations in Jenkins match what would be generated")

if __name__ == '__main__':
    main()
