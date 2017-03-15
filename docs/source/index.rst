unleash-client-python
=====================

Unleash is a feature toggle system with a good design and simple API.

This is a Python client library for that system, for use in applications and
services. It seems to work well enough, but there's are a number of issues,
consider it alpha for now.

The main project is at https://github.com/Unleash/unleash.


.. x Contents:
.. x
.. x .. toctree::
.. x    :maxdepth: 2

Getting Started
---------------

To use, create a `Client` instance with at least the URL of the Unleash
server, and use

   >>> import unleash
   >>> features = unleash.Client(url='https://unleash.herokuapp.com')

The client can then be passed around and queried:

   >>> context = {'user_id': ..., }
   >>> features.enabled('feature', context)
   False


License
-------

Python Unleash is released under the Apache License, version 2.0.

.. x Indices and tables
.. x ==================
.. x
.. x * :ref:`genindex`
.. x * :ref:`modindex`
.. x * :ref:`search`
