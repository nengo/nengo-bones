***************
Release History
***************

.. Changelog entries should follow this format:

   version (release date)
   ======================

   **section**

   - One-line description of change (link to Github issue/PR)

.. Changes should be organized in one of several sections:

   - Added
   - Changed
   - Deprecated
   - Removed
   - Fixed

0.2.1 (May 24, 2019)
====================

**Added**

- Added ``codespell_ignore_words`` option to ``static.sh.template``,
  which is a list of words that ``codespell`` will ignore. (`#35`_)
- Added ``analytics_id`` option to ``docs_conf.py.template``,
  which will enable Google Analytics tracking. (`#35`_)

**Changed**

- ``codespell`` will now ignore ``_vendor`` directories. (`#36`_)

**Fixed**

- Fixed an issue with ``static.sh.template`` in which Python files
  that were not converted from notebooks were deleted. (`#16`_)

.. _#16: https://github.com/nengo/nengo-bones/pull/16
.. _#35: https://github.com/nengo/nengo-bones/pull/35
.. _#36: https://github.com/nengo/nengo-bones/pull/36

0.2.0 (May 15, 2019)
====================

**Added**

- Added ``apt_install`` option that can be set in the ``jobs`` section to
  ``apt install`` any custom ``apt`` requirements for a job. (`#14`_)
- Added templates for ``CONTRIBUTING.rst``, ``CONTRIBUTORS.rst``,
  ``LICENSE.rst``, ``MANIFEST.in``, ``docs/conf.py``, ``setup.cfg``, and
  ``setup.py`` (`#17`_)
- Templates will now be automatically loaded from a ``<repo>/.templates``
  directory if it exists. When overriding existing templates, the built-in
  templates can be accessed in ``include`` and ``extend`` tags with the
  ``templates/`` prefix. (`#17`_)
- Added ``flake8`` to the static check script. (`#17`_)
- Added the ``bones-pr-number`` script to predict the next PR number for a
  repository. This helps when writing a changelog entry before a PR has been
  made. (`#18`_)

**Changed**

- The Python version is now specified by the ``python`` option (instead of
  ``python_version``), for consistency with ``.travis.yml``. (`#14`_)
- All ``nengo-bones`` scripts now start with ``bones-``, to make them easier
  to find with autocompletion. ``generate-bones`` is now ``bones-generate``,
  and ``check-bones`` is now ``bones-check``. (`#18`_)

**Removed**

- Removed ``conda`` from the CI setup; all installations should be done
  through ``pip`` instead. (`#14`_)
- Removed the ``--template-dir`` option from the ``generate-bones`` script;
  use a ``.templates`` directory instead. (`#17`_)

**Fixed**

- Order of templated dicts should now be deterministic for
  all Python versions. (`#14`_)

.. _#14: https://github.com/nengo/nengo-bones/pull/14
.. _#17: https://github.com/nengo/nengo-bones/pull/17
.. _#18: https://github.com/nengo/nengo-bones/pull/18

0.1.0 (April 15, 2019)
======================

Initial release of Nengo Bones!
Thanks to all of the contributors for making this possible!
