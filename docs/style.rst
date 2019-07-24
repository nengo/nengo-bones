***********
Style guide
***********

Nengo Bones attempts to enforce
as much of this style guide as possible.
However, since not everything can be automatically enforced,
all Nengo developers should be familiar with this style guide
and follow it when working on Nengo projects.

Python
======

We use ``black`` for automated formatting.
We recommend that you set up your editor to run ``black``
when you save a Python file;
see `Black editor integration
<https://black.readthedocs.io/en/stable/editor_integration.html>`__
for details on how to do that.

Whether you set up ``black`` with your editor or not,
you should run ``black`` through a pre-commit hook.
To do this, first `install pre-commit <https://pre-commit.com/#install>`__.
Then, run

.. code-block:: bash

   pre-commit install

to install ``black`` and any other pre-commit hooks
that a project is using.

We use ``flake8`` and ``pylint`` for automated checks.
The exact options may vary from project to project,
so the easiest way to run these checks is to
run the ``.ci/static.sh`` script locally.

.. code-block:: bash

   bones-generate --output-dir .ci ci-scripts && .ci/static.sh script

If you are missing any required packages,
running ``.ci/static.sh install`` should install all requirements.

Class member order
------------------

In general, we stick to the following order for members of Python classes.

1. Class-level member variables (e.g., ``nengo.Ensemble.probeable``).
2. Parameters (i.e., instances of ``nengo.params.Parameter``)
   with the parameters in ``__init__`` going first in that order,
   then parameters that don't appear in ``__init__`` in alphabetical order.
   All these parameters should appear in the Parameters section of the docstring
   in the same order.
3. ``__init__``
4. Other special (``__x__``) methods in alphabetical order,
   except when a grouping is more natural
   (e.g., ``__getstate__`` and ``__setstate__``).
5. ``@property`` properties in alphabetical order.
6. ``@staticmethod`` methods in alphabetical order.
7. ``@classmethod`` methods in alphabetical order.
8. Methods in alphabetical order.

"Hidden" versions of the above (i.e., anything starting with an underscore)
should either be placed right after they're first used,
or at the end of the class.

.. note:: These are guidelines that should be used in general,
          not strict rules.
          If there is a good reason to group differently,
          then feel free to do so, but please explain
          your reasoning in a code comment or commit message.

Docstrings
----------

We use ``numpydoc`` and
`NumPy's guidelines for docstrings
<https://github.com/numpy/numpy/blob/master/doc/HOWTO_DOCUMENT.rst.txt>`_,
as they are readable in plain text and when rendered with Sphinx.

We use the default role of ``obj`` in documentation,
so any strings placed in backticks in docstrings
will be cross-referenced properly if they
unambiguously refer to something in the Nengo documentation.
See `Cross-referencing syntax
<https://www.sphinx-doc.org/en/master/usage/restructuredtext/roles.html#cross-referencing-syntax>`_
and the `Python domain
<https://www.sphinx-doc.org/en/master/usage/restructuredtext/domains.html#the-python-domain>`_
for more information.

Git
===

We use several advanced ``git`` features that
rely on well-formed commit messages.
Commit messages should fit the following template.

.. code-block:: none

   Capitalized, short (50 chars or less) summary

   More detailed body text, if necessary.  Wrap it to around 72 characters.
   The blank line separating the summary from the body is critical.

   Paragraphs must be separated by a blank line.

   - Bullet points are okay, too.
   - Typically a hyphen or asterisk is used for the bullet, followed by
     single space, with blank lines before and after the list.
   - Use a hanging indent if the bullet point is longer than a
     single line (like in this point).

.. todo:: JS, TS, CSS, HTML, etc
