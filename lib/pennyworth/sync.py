#!/usr/bin/python3

import pennyworth.command
import pennyworth.host
import pennyworth.integrate
import pennyworth.job_config


def _apply_jobs(host, jenkins_configs, generated_configs):
    def _handler(name, first, second):
        if first and second:
            # both exist, so update jobs
            host.change_job(name, second)
        else:
            # only one exists
            if first:
                # job was removed
                host.erase_job(name)
            else:
                # new job
                host.create_job(name, second)

    pennyworth.integrate.compare(jenkins_configs, generated_configs, _handler)


class SyncCommand(pennyworth.command.HostCommand):
    def __init__(self):
        super().__init__(prog="pennyworth sync",
                         description="Sync generated configurations with "
                                     "Jenkins")

    def process(self, parsed_args):
        host = self.make_host(parsed_args)
        jenkins_configs = pennyworth.host.get_host_configs(host)
        generated_configs = pennyworth.job_config.generate_configs()
        _apply_jobs(host, jenkins_configs, generated_configs)


def main(args=None):
    # pylint: disable=missing-docstring
    sync = SyncCommand()
    pennyworth.command.execute_command(sync, args)


_SYNC_COMMAND = (main, "Sync generated job configuratiosn with Jenkins")

if __name__ == '__main__':
    main()
