***************
Making releases
***************

These instructions assume that
your project is using Nengo Bones
to generate CI scripts,
in particular the ``deploy.sh`` script.

Python projects
===============

In the following steps, ``X.Y.Z`` is the new version number.

1. Start a release candidate branch.

   1. Switch to ``master`` and ensure it is up-to-date by doing ``git pull``.

   2. Create a new branch off of ``master`` with

      .. code-block:: bash

         git checkout -b release-candidate-X.Y.Z

2. Verify the repository is in a release-ready state.

   The exact procedure will depend on the repository
   and how many changes have occurred since the last release,
   but may include the following steps.

   1. Run all tests to ensure they pass on all supported platforms,
      including slow tests that are normally skipped.
      The command will depend on the repository,
      but for Nengo core it's

      .. code-block:: bash

         pytest --pyargs nengo --plots --analytics --logs --slow

   2. Review all of the outputs (e.g., plots)
      generated from the test suite for abnormalities.

   3. Build documentation and review it for abnormalities.

   4. Commit all changes from the above steps with appropriate messages.

3. Make a release commit.

   1. Change the version information for your project.
      For most Python projects, it lives in ``project/version.py``.
      See that file for details.

   2. Set the release date in the changelog, ``CHANGES.rst``.

   3. Commit all changes from the above steps with

      .. code-block:: bash

         git commit -m "Release vX.Y.Z"

4. Push the release candidate branch.

   This will start a TravisCI build that will run several checks
   to verify that the repository is in a good state for release.

   1. If the build fails, fix any issues and commit the changes
      such that they appear before the release commit in ``git log``.

   2. When the TravisCI build succeeds,
      inspect the release and associated metadata and files at,
      e.g., https://test.pypi.org/project/nengo

      In particular, make sure that extraneous files are not
      included in the released files.
      File sizes give a good indication of whether
      extra files are present.

      If there are any issues, fix them and commit them before
      the release commit.

   3. *Optional:*
      Make a pull request on the release candidate branch
      to solicit reviews.

      This should be done if any non-trivial changes were made
      in the previous steps, or if the release includes
      many changes that should be verified on multiple machines.
      Use your best judgment and consult with your team if unsure.

5. Release to PyPI.

   1. Tag the release commit with the version number; i.e.,

      .. code-block:: bash

         git tag -a vX.Y.Z

      We use annotated tags to retain authorship information.
      If you wish to provide a message with information about the release,
      feel free, but it is not necessary.

   2. Push the tag with

      .. code-block:: bash

         git push origin vX.Y.Z

      Pushing the tag will trigger another TravisCI build
      that will deploy the release and updated documentation.

   3. Confirm the release has been done successfully
      at, e.g., https://pypi.org/project/nengo
      once the TravisCI build is complete.

6. Start the next version.

   1. Change the version information in ``project/version.py``.

   2. Make a new changelog section in ``CHANGES.rst``
      in order to collect changes for the next release.

   3. ``git add`` the changes above and commit with

      .. code-block:: bash

         git commit -m "Starting development of vX.Y.Z+1"

   4. *Optional:*
      If you opened a PR on the release candidate branch,
      push it to Github so it will be marked as merged.

   5. Merge the release candidate branch into ``master``
      and push the ``master`` branch.

   6. Delete the release candidate branch locally and remotely.

7. Announce the new release.

   1. Copy the changelog into the tag details on the
      Github release tab.
      Note that the changelog is in reStructuredText,
      while Github expects Markdown.
      Use `Pandoc <https://pandoc.org/try/>`_
      to convert between the two formats
      with the following command:

      .. code-block:: bash

         pandoc -t gfm -f rst CHANGES.rst

   2. Write a release announcement.
      Generally, it's easiest to start from
      the last release announcement
      and change it to make sense with the current release
      so that the overall template of each announcement is similar.
      Post the release announcement on the
      `forum <https://forum.nengo.ai/c/general/announcements>`_.

   3. Make a PR on the
      `ABR website repo <https://github.com/abr/abr.github.io>`__
      modifying a file in the ``_releases`` folder to
      point to the announcement post on the forum.
