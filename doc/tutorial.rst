Tutorial
########

Getting started
===============

Getting an API key
------------------
First and foremost, you'll need a Steam API key. You can get one `here <https://steamcommunity.com/dev/apikey>`_.


Initialize wrapper via environment variable
-------------------------------------------
Create a new environment variable ``D2_API_KEY`` and set its value to the API key. You can then, just use
the following code to initialize the wrapper. ::

    api = d2api.APIWrapper()
    
Initialize wrapper inline
-------------------------
Literally just initialize the wrapper inline. That's about it. ::

    # overrides the environment variable key
    api = d2api.APIWrapper('YOUR_API_KEY')

Unparsed response
-----------------
There's a good chance you'd like your responses au naturel. Just set ``parse_response = False``. 
The wrapper returns the response text as is (without using the built-in json parser). ::

    api = d2api.APIWrapper(api_key = 'YOUR_API_KEY', parse_response = False)

.. note::
    While it is highly recommended that a json response have unique key-value pairs, it is not mandatory that they be unique. 
    Some responses of the Steam WebAPI consists of such repeated key-value pairs. Use ``d2api.src.util.decode_json`` to parse 
    these results to avoid losing content.

.. _tutorial-examples:

Examples
========

Hero frequency in last 100 games
--------------------------------
.. literalinclude:: example1.py

Using the API without the API
-----------------------------
.. literalinclude:: example2.py

Matches without leavers
-----------------------
.. literalinclude:: example3.py

