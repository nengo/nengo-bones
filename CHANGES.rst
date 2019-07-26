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

0.4.1 (July 26, 2019)
=====================

**Added**

- Added ``allclose_tolerances`` option to the ``pytest`` section of the
  ``setup.cfg`` template to set tolerances for pytest-allclose. (`#47`_)

.. _#47: https://github.com/nengo/nengo-bones/pull/47

0.4.0 (July 26, 2019)
=====================

**Added**

- Added style guide and release instructions to documentation. (`#44`_)
- Added templates for ``.pre-commit-config.yaml`` and ``pyproject.toml``
  so downstream repositories can easily adopt Black. (`#49`_)

**Changed**

- We now check that Python source files are autoformatted with Black
  in the ``static.sh`` script. (`#49`_)
- Templates will now be autoformatted with Black during the rendering
  process, if Black is installed. (`#49`_)
- Take advantage of multiprocessing to speed up pylint static checks. (`#49`_)
- The ``E203`` flake8 check and ``bad-continuation`` pylint check are now
  disabled by default. (`#50`_)

.. _#44: https://github.com/nengo/nengo-bones/pull/44
.. _#49: https://github.com/nengo/nengo-bones/pull/49
.. _#50: https://github.com/nengo/nengo-bones/pull/50

0.3.0 (July 19, 2019)
=====================

**Added**

- The ``nengo_bones.templates`` module was added to consolidate code
  that loads and renders templates. (`#45`_)

**Changed**

- The ``docs/conf.py`` template has been updated for new versions of
  Nengo Sphinx Theme. (`#46`_)
- ``static.sh`` and ``examples.sh`` will now check any notebooks in the
  ``docs`` folder (not just ``docs/examples``). (`#46`_)
- ``bones-check`` now checks that the content of the generated files
  matches the expected content, rather than relying on version numbers.
  This means most files will not need to be regenerated when new Nengo Bones
  versions are released, and that ``bones-check`` will be sensitive to changes
  within a dev version. (`#45`_)

**Fixed**

- The ``static.sh``/``examples.sh`` script will no longer fail if there are no
  notebooks in the ``docs`` folder. (`#46`_)

.. _#45: https://github.com/nengo/nengo-bones/pull/45
.. _#46: https://github.com/nengo/nengo-bones/pull/46

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
