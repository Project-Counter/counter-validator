=========================
Development documentation
=========================


Technologies used
=================

The application consists of a backend and frontend parts connected via a RESTful API.

Backend technologies:

* Python
* Django
* Django REST Framework
* Celery
* PostgreSQL
* Redis

Frontend technologies:

* Typescript
* Vue 3
* Vuetify 3


Development setup
=================

This section describes how to setup the development environment. It presumes that you have some
knowledge of Python, virtual environments, etc.

To start the development environment, you need start the following:

Django server
~~~~~~~~~~~~~

.. code-block:: bash

   python manage.py runserver localhost:8028

The choice of port is arbitrary, but you need to tell the frontend to use the same port.

Frontend
~~~~~~~~

.. code-block:: bash

   yarn dev --port 3030

The port above is up to you - it is the port where the frontend will be served. If you wish to pass
backend port, you have to do it using an env variable ``VITE_BE_PORT`` like this:

.. code-block:: bash

   VITE_BE_PORT=8028 yarn dev --port 3030

Celery server
~~~~~~~~~~~~~

.. code-block:: bash

   sh celery_devel.sh

C5Tools server
~~~~~~~~~~~~~~

For this you will need the ``c5tool`` package which is available in a separate repository. When you
get it, you need to start the docker container with the following command:

.. code-block:: bash

   docker compose up

It will start a container with the ``c5tools`` server which will listen to port 8180 by default.
You can pass this port to the backend using an env variable ``VALIDATION_MODULES_URLS`` in the .env
file in the root of the project. For example like this:

.. code-block:: bash

   VALIDATION_MODULES_URLS=http://localhost:8180

Registry data
~~~~~~~~~~~~~

To enable selection of platform from the COUNTER registry, the data must be loaded into the database
first. To do this, run the following command:

.. code-block:: bash

   python manage.py download_registry


Note on VSCode
==============

The project contains a basic configuration for VSCode. It includes two launch configurations for
Django and Vue. So you can run the Django server and the frontend server using the debugger
directly from VSCode.
