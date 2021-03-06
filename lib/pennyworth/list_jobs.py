#!/usr/bin/python3

import pennyworth.command


class ListJobsCommand(pennyworth.command.HostCommand):
    def __init__(self):
        super().__init__(prog="pennyworth list-jobs",
                         description="List all jobs")

    def process(self, parsed_args):
        #print("{}\n\n{}".format(host, parsed_args))
        host = self.make_host(parsed_args)
        for name in sorted(i[0] for i in host.list_jobs()):
            print(name)


def main(args=None):
    # pylint: disable=missing-docstring
    list_jobs = ListJobsCommand()
    pennyworth.command.execute_command(list_jobs, args)


_LIST_JOBS_COMMAND = (main, "List all jobs")

if __name__ == '__main__':
    main()
