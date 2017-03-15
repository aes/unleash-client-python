unleash-client-python
=====================

Unleash is a feature toggle system with a good design and simple API.

This is a Python client library for that system, for use in applications and
services. It seems to work well enough, but there's are a number of issues,
consider it alpha for now.

The main project is at https://github.com/Unleash/unleash.


Overview
--------

Client for the Unleash feature toggle service

Installation / Usage
--------------------

<!--
To install use pip:

    $ pip install unleash-client
-->

To clone the repo:

    $ git clone https://github.com/aes/unleash-client-python.git
    $ python setup.py install
    
CLI tool
--------
To ask a specific feature test:

    $ python -m unleash_client feature.name user_id=bleh

To try the demo cli tool

    $ python -m unleash_client --demo --sleep 0.05 feature.name user_id=%

Contributing
------------

TBD

Example
-------

TBD

See License.txt for Apache License v2.0

Copyright (c) 2017 Anders Eurenius
