COUNTER Validation Tool
=======================

This repository contains the COUNTER Validation Tool source code.

It is licensed under the `Apache License, Version 2.0 <https://www.apache.org/licenses/LICENSE-2.0>`_.

Copyright 2025, `The COUNTER Metrics Limited <https://www.countermetrics.org/>`_.

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.



Status
------

The application is still a work in progress. As is the documentation which
is mostly development oriented at present. It will be updated when the
application is ready.


Technologies used
-----------------

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


Documentation
-------------

The documentation is available in the `docs directory <docs/index.rst>`_.


Development notes
-----------------

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
