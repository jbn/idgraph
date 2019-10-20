idgraph
=======

.. image:: https://img.shields.io/pypi/v/idgraph.svg
        :target: https://pypi.python.org/pypi/idgraph

.. image:: https://travis-ci.org/jbn/idgraph.svg?branch=master
        :target: https://travis-ci.org/jbn/idgraph


Provides IPython cell magic for `dgraph <https://dgraph.io/>`__ remote
interaction.

Installation
------------

.. code:: bash

    pip install idgraph

Why is this?
------------

While `dgraph <https://dgraph.io>`__ provides several useful interfaces,
I spend most of my time learning, exploring, and developing in
`Jupyter <https://jupyter.org/>`__. Executable documentation is
fantastic! This package abstractly provides cell magic for dgraph query,
mutation, and alteration execution. You could do the same with ``curl``
or ``requests``. But, the sensible defaults help make things less
verbose and tedious. (It's inspired by my experience with
`itikz <https://github.com/jbn/itikz>`__ which proved really
beneficial.)

Usage
-----

The easiest way to understand how this works is by following (and cloning)
the `tutorial notebook <https://github.com/jbn/idgraph/blob/master/tutorial.ipynb>`__.
It's a projection dgraph's
`Tour of Dgraph: A Bigger Dataset <https://tour.dgraph.io/moredata/1/>`__.

Cheat Sheet
~~~~~~~~~~~

Load the extension with,

.. code::

    %load_ext idgraph

Then,

-  By default, ``%%dgraph`` assumes a query.

   -  ``%%dgraph --alter`` does an alteration
   -  ``%%dgraph --mutate`` does a mutation

-  By default, ``%%dgraph`` assumes ``localhost:8080``

   -  ``%%dgraph --addr=remote-host:8080`` overrides the default
   -  The ``DGRAPH_ADDR`` environmental variable overrides default if
      the ``--addr`` flag isn't set

-  By default, only the value associated with the ``data`` key in the
   response is shown.

   -  ``%%dgraph --full-resp`` shows the full response including
      metadata.
   -  ``%%dgraph --jmespath="query"`` allows you to extract part of the
      response with a `jmespath <http://jmespath.org/>`__ query.

-  By default, each cell execution binds the extracted response to
   ``_dgraph`` and the full response to ``_dgraph_full``

   -  ``%%dgraph --into=name`` will bind the extracted response to
      ``name`` and the full response to ``{name}_full``

-  By default, the cell contents are executed.

   -  ``%%dgraph --skip`` skips execution.

      -  Useful for mutations that are possibly dangerous on someone
         else's computer.

-  Jinja

   -  technically you can use templates in a directory. you almost
      certainly shouldnt though.

Credits
~~~~~~~

This package was created with
`Cookiecutter <https://github.com/audreyr/cookiecutter>`__ and the
`audreyr/cookiecutter-pypackage <https://github.com/audreyr/cookiecutter-pypackage>`__
project template.
