pennyworth
==========
|codacy|
|code-climate|

pennyworth is a set of scripts to make it easier to manage Jenkins_ job
configurations.

The project is named after Batman's butler, Alfred Pennyworth.  Since Jenkins
uses a butler as their icon and Alfred is a butler, he seemed a good person to
name the project after.  Alfred was too generic a name, but nothing showed up
in PyPi_ when I searched for "pennyworth".


Motivation
----------
I wrote a hacky shell script a while ago to create Jenkins jobs based on my
needs, but it fell apart once I needed to update configurations and suddenly my
templates didn't work (different dependencies, different build triggers, etc.).
The idea here is that while every job may still be a special snowflake, the
pieces are stil pretty similar in most cases.


Installation
------------
The easiest way to install is using pip_.

.. code:: bash

    $ cd /path/to/pennyworth
    $ pip3 install .

Eventually I'll publish something to PyPi, and then a command like the
following will work:

.. code:: bash

    $ pip3 install pennyworth


Using
-----
pennyworth uses sub-commands to perform various tasks.  The built-in
sub-commands are:

* `build-jobs`_
* `list-jobs`_
* `validate`_


.. |codacy| image:: https://api.codacy.com/project/badge/Grade/d457ee2e8da847ba9d91e5357f0ccf06
    :target: https://www.codacy.com/app/snewell/pennyworth?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=snewell/pennyworth&amp;utm_campaign=Badge_Grade

.. |code-climate| image:: https://api.codeclimate.com/v1/badges/ba74354c7be92cc5619f/maintainability
   :target: https://codeclimate.com/github/snewell/pennyworth/maintainability
   :alt: Maintainability

.. _Jenkins: https://jenkins.io
.. _pip: https://pypi.python.org/pypi/pip
.. _PyPi: https://pypi.python.org

.. _build-jobs: docs/commands/build-jobs.rst
.. _list-jobs: docs/commands/list-jobs.rst
.. _validate: docs/commands/validate.rst
