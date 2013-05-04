========
Overview
========

Django
======

**ProsDataBase** is based on `Django <https://www.djangoproject.com/>`_, a python web-framework.
The `Django documentation <https://docs.djangoproject.com/>`_ is detailed
and we recommend the `Tutorial <https://docs.djangoproject.com/en/1.5.1/intro/tutorial01/>`_.

Assuming you know the Basics (models, views, urls) we can start with the special characteristics
of the **ProsDataBase** project.

The source code for this project is located in ``prosdatabase/``. Note that Django 1.5.1 comes with a new
directory structure. You find the project related files in ``prosdatabase/prosdatabase/``.

By now there are the following custom apps:

* :doc:`herobase` blabalba

Deployment
==========

We use `south <http://south.readthedocs.org>`_ for database migrations.

.. NOTE::
   If you get an database related error after pulling the git repo, it may be necessary to
   migrate one of the custom apps. Try::

      $ prosdatabase/managy.py migrate



Apart from that you can push your **tested** commits to the ``git repo`` and they will be
automatically deployed on the develoment server.

Tests
=====

**ProsDataBase** uses the `unittest module <http://docs.python.org/library/unittest.html>`_.
Tests are located in

* :py:mod:`herobase.tests`


`Django-coverage <https://bitbucket.org/kmike/django-coverage/>`_ generates
`html <https://youarehero.net/coverage/>`_ with information about the test coverage of the project.

More documentation follows...

Other Components
================

Beside *Django* and the *project related apps* there are other components used in this project:

* This documentation is build with `sphinx <http://sphinx.pocoo.org/contents.html>`_.
  The documentation source is located in ``docs/``.
