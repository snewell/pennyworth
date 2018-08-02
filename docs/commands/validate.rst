validate
========

Synopsis
--------
::

    pennyworth validate [-h] [--host HOST] [--folder FOLDER]


Description
-----------
Generate diffs between job configurations in Jenkins and what pennyworth
generates.  Output will be in unified diff format, and jobs that would be
added/removed should reflect that in the diff output (i.e., all lines prefixed
with either a - or +).

The configurations in Jenkins will be treated as the original version and the
generated configurations will be treated as new.


Options
-------
  -h, --help       show this help message and exit
  --host HOST      The host to use. If unspecified, the first host listed in
                   the host configuration file will be used.
  --folder FOLDER  The folder to operate in. (default: None)
