#!/usr/bin/python3

"""Code to support the build-jobs command."""

import argparse

import pennyworth.command
import pennyworth.job_config


def _verify_legal_jobs(requested, available):
    for job in requested:
        if job not in available:
            raise Exception("{} is not a valid job".format(job))


def _generate_configs(job_config, jobs):
    generated_configs = {}
    chunk_cache = pennyworth.job_config.ChunkCache()
    for job in jobs:
        config = pennyworth.job_config.build_config(
            job_config.get_job_chunks(job), chunk_cache,
            job_config.get_job_subs(job))
        generated_configs[job] = config
    return generated_configs


class BuildJobsCommand(pennyworth.command.Command):
    """
    Class to implement the build-jobs command.
    """

    def __init__(self):
        super().__init__(prog="pennyworth build-jobs",
                         description="Build job configurations")
        self.add_argument("jobs", nargs="*", default=argparse.SUPPRESS,
                          help="The jobs to generate")

    def process(self, parsed_args):
        """
        Process command-line arguments and execute the command.

        Arguments
        parsed_args - Parsed command-line arguments
        """
        job_config = pennyworth.job_config.make_configs('jobs.conf')
        available_jobs = job_config.get_jobs()
        if 'jobs' in parsed_args:
            _verify_legal_jobs(parsed_args.jobs, available_jobs)
            jobs = parsed_args.jobs
        else:
            jobs = job_config.get_jobs()
        generated_configs = _generate_configs(job_config, jobs)
        for name, config in generated_configs.items():
            print(name)
            print('-' * len(name))
            print(config)


def main(args=None):
    # pylint: disable=missing-docstring
    build_jobs = BuildJobsCommand()
    pennyworth.command.execute_command(build_jobs, args)


_BUILD_JOBS_COMMAND = (main, "Build job configurations")

if __name__ == '__main__':
    main()
