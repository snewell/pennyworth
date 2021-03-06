#!/usr/bin/python3

import argparse
import errno
import sys

import pennyworth.host


class Command:
    def __init__(self, *args, **kwargs):
        self.parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            *args, **kwargs)

    def add_argument(self, *args, **kwargs):
        self.parser.add_argument(*args, **kwargs)

    def execute(self, *args, **kwargs):
        parsed_args = self.parser.parse_args(*args, **kwargs)
        self.process(parsed_args)

    def process(self, parsed_args):
        pass


def _get_host(host):
    host_list = pennyworth.host.get_hosts()
    if host_list:
        if host:
            if host in host_list.sections():
                return host_list[host]
            raise Exception("{} not a valid host".format(host))
        return host_list[host_list.sections()[0]]
    raise Exception("No hosts in listed")


class HostCommand(Command):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_argument("--host",
                          default=argparse.SUPPRESS,
                          help="The host to use.  If unspecified, the first "
                               "host listed in the host configuration file "
                               "will be used.")
        self.add_argument("--folder",
                          default=None,
                          help="The folder to operate in.")

    @staticmethod
    def make_host(parsed_args):
        hostname = None
        if 'host' in parsed_args:
            hostname = parsed_args.host
        host = _get_host(hostname)
        return pennyworth.host.make_host(host, parsed_args.folder)

    def process(self, parsed_args):
        pass


def execute_command(command, args):
    """
    Runs the provided command with the given args.  Exceptions are propogated
    to the caller.
    """
    if args is None:
        args = sys.argv[1:]
    try:
        command.execute(args)

    except IOError as failure:
        if failure.errno == errno.EPIPE:
            # This probably means we were piped into something that terminated
            # (e.g., head).  Might be a better way to handle this, but for now
            # silently swallowing the error isn't terrible.
            pass
        else:
            print("Error: {}".format(str(failure)), file=sys.stderr)

    except Exception as failure:
        print("Error: {}".format(str(failure)), file=sys.stderr)
        sys.exit(1)
