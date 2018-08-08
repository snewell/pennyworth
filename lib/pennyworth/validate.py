#!/usr/bin/python3

import difflib

import pennyworth.command
import pennyworth.host
import pennyworth.job_config


def _print_diff(name, jenkins_lines, generated_lines):
    diffs = difflib.unified_diff(jenkins_lines, generated_lines,
                                 "jenkins/{}".format(name),
                                 "generated/{}".format(name))
    for diff in diffs:
        # The issue that control lines (file lines, line offsets) have a
        # trailing newline but the actual diff lines (both differences and
        # context lines) do not.  Since some of the diff tools I've trid get
        # unhappy when there are extra lines, this tries to make sure we don't
        # print two newlines when it's a control line.
        if diff[-1] == '\n':
            print(diff, end='')
        else:
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
        jenkins_configs = pennyworth.host.get_host_configs(host)
        generated_configs = pennyworth.job_config.generate_configs()
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
