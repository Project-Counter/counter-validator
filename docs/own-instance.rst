=========================
Running your own instance
=========================

We recommend using the public instance at `https://validator.bigdigdata.com <https://validator.bigdigdata.com>`_.

However, if you for some reason want to run your own instance, we have you covered. You will find the necessary information below.

Running from source
-------------------

You can download the source code from `GitHub <https://github.com/Project-Counter/counter-validation-tool>`_ and run it locally.
It is written in Python in combination with Vue for the frontend. It will require some additional setup to get it running, like
creating a database and setting up a virtual environment.

At present, we do not provide any installation instructions, but if you have experience with running Python, and especially Django,
applications, you should be able to figure it out.


Using Docker
------------

The easiest way to run the COUNTER Validation Tool is by using Docker. Because the application comprises of several components,
it uses Docker Compose to make it easy to spin up all the necessary services.

This method is currently in preparation and will be documented here in the future.
