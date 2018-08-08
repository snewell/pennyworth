#!/usr/bin/python3

import pennyworth.command
import pennyworth.host
import pennyworth.job_config


def _apply_jobs(host, jenkins_configs, generated_configs):
    for name, config in jenkins_configs.items():
        if name in generated_configs:
            generated_config = generated_configs[name]
            del generated_configs[name]
            if config != generated_config:
                # update job
                host.change_job(name, generated_config)
        else:
            # job was removed
            host.erase_job(name)

    # everything left is a new job
    for name, config in generated_configs.items():
        host.create_job(name, config)


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
