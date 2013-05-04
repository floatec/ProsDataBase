==================
Installation Guide
==================

This section describes how to set up a local development environment for the **You are HERO** project.
Since ``python`` is a platform independent language, it should be possible on most operating systems.
However, the focus of this document is on Unix based systems like MacOS or Ubuntu/linux.

Preparation and Dependencies
============================

First of all you need `python 2.7 <http://www.python.org/download/>`_ and
the version control system `git <http://git-scm.com/book/en/Getting-Started-Installing-Git>`_.
On most Unix based systems ``python`` is already installed

You may use your operating system's package manager::

   $ sudo apt-get install git


or on MacOS::

   coming soon...

Cloning the git repository
==========================

    $ git clone https://github.com/floatec/MEPSS2013.git


The bootstrap script
====================

After cloning the git repository, browse to your project dir and run::

    $ sudo pip install -r deploy/requirements.txt



T



Initialize Database
===================

For developing purposes the default Database engine is `sqlite <http://www.sqlite.org/docs.html>`_,
so you don't have to set up a custom database. Run::

    (env)$ src/manage.py syncdb
    (env)$ src/manage.py migrate

for initializing the local database. If you were asked to create a superuser, do so and continue.
You will need this user to log into the ``django-admin`` and it is also your first hero.

Start Development Server
========================

Now you are ready to test your installation::

    (env)$ src/manage.py runserver

Try to visit `localhost on port 8000 <http://localhost:8000>`_. If everything is
working correctly you should see your local **prosDataBase** instance.

