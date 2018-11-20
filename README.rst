***********
Nengo bones
***********

This repository provides the bones for new Nengo projects.
New projects can start with these bones,
or existing projects can refer back to here
when adopting more Nengo project conventions.

Generally, strings that should be replaced with
a project-specific string are capitalized
and enclosed in double curly brackets ``{{ LIKE THIS }}``.
The capitalization makes them stick out;
the curly brackets are easy to ``grep`` for,
and are inspired by Jinja templates.

Plans
=====

Currently this repository contain bones
that must be manually inspected,
modified, and incorporated into Nengo projects.
In the future, we plan to automate
as much of this process as possible
so that projects can continue to have
healthy bones as this repository develops.
Doing this in an error-free way that relieves,
rather than adds to, maintainer burden is tricky.

Notes
=====

Some of the bones require the following steps
to be done outside of the repository.

1. Set up the ``GH_TOKEN`` environment variable through TravisCI.
