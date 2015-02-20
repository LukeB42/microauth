Keys
=====================================

Key creation is a simple PUT request to **/v1/keys**, with a name field specifying the name of your program.

This helps the administrator, which may well be you!

Creating
-----------------
**PUT** takes only one argument in the request body, a **name** field.
The name cannot contain whitespace and must be less than 60 characters.

.. code-block:: javascript

	$ http --verify=no put https://localhost:7789/v1/keys Authorization:"Basic \$2a\$12\$R0yq8EOnxgWTuIuEPwwbsusQ8qgLTYSpUhpuhJjbw0mDHJZN9ERZm" name=NewApp
	HTTP/1.0 201 CREATED
	Content-Encoding: gzip
	Content-Length: 144
	Content-Type: application/json
	Date: Thu, 19 Feb 2015 11:17:11 GMT
	Server: Werkzeug/0.10.1 Python/2.7.3
	Vary: Accept-Encoding

	{
	    "active": true, 
	    "apikey": "$2a$12$xVOCuxixOd9ly/xiUlWqg.7mIa05Dk/bcT4DykvePiVLDjjEy2zbu", 
	    "name": "NewApp", 
	    "systemwide": null
	}

These requests require the master key when **permit_new** is disabled.

Modifying
-----------------
**POST** is for administrative tasks involving modifying individual keys or setting whether anonymous clients can
generate their own API keys.

* **name** or **key** can be used to identify the target key to alter.
* **key** in conjunction with **name** can be used to change an API key's name.
* **systemwide** determines whether the target key can access keyless objects.
* **active** determines whether an API key will authenticate.
* **global_delete** determines whether a *systemwide* key can delete global objects.
* **permit_new** determines whether anonymous clients can create keys for themselves.


Reviewing
-----------------
.. http:get:: /v1/keys

	This will furnish you with information about your key, like the names of objects it owns and whether it has access to global objects.

	For instance if we use the key generated in the :doc:`administration` section:

	.. code-block:: javascript

		$ http --verify=no https://localhost:7789/v1/keys Authorization:"Basic \$2a\$12\$xVOCuxixOd9ly/xiUlWqg.7mIa05Dk/bcT4DykvePiVLDjjEy2zbu"
		HTTP/1.0 200 OK
		Content-Encoding: gzip
		Content-Length: 111
		Content-Type: application/json
		Date: Thu, 19 Feb 2015 11:52:01 GMT
		Server: Werkzeug/0.10.1 Python/2.7.3
		Vary: Accept-Encoding

		[
		    {
		        "active": true, 
		        "name": "NewApp", 
		        "privileges": [], 
		        "roles": [], 
		        "systemwide": null, 
		        "users": []
		    }
		]

	There is no information on whether this key can delete objects in the global namespace yet because the **systemwide** bit isn't set.

.. http:get:: /v1/keys/(name)

	This is an administrative endpoint for the master key to consume data about specific keys.

	.. code-block:: javascript

		$ http --verify=no https://localhost:7789/v1/keys/NewApp Authorization:"Basic \$2a\$12\$R0yq8EOnxgWTuIuEPwwbsusQ8qgLTYSpUhpuhJjbw0mDHJZN9ERZm"
		HTTP/1.0 200 OK
		Content-Length: 209
		Content-Type: application/json
		Date: Thu, 19 Feb 2015 11:59:30 GMT
		Server: Werkzeug/0.10.1 Python/2.7.3

		{
		    "active": true, 
		    "apikey": "$2a$12$xVOCuxixOd9ly/xiUlWqg.7mIa05Dk/bcT4DykvePiVLDjjEy2zbu", 
		    "name": "NewApp", 
		    "privileges": [], 
		    "roles": [], 
		    "systemwide": null, 
		    "users": []
		}

Deleting
-----------------
.. http:delete:: /v1/keys

	This permits users to delete their own keys, or for the master key to delete another key.

	To do this, specify the key string as **key** in the request body.

	Objects belonging to the target key can also be reparented to the global namespace by specifying a value for **reparent** in the request body, assuming the key has the systemwide bit set.

	.. code-block:: javascript

		$ http --verify=no delete https://localhost:7789/v1/keys Authorization:"Basic \$2a\$12\$xVOCuxixOd9ly/xiUlWqg.7mIa05Dk/bcT4DykvePiVLDjjEy2zbu" key=\$2a\$12\$xVOCuxixOd9ly/xiUlWqg.7mIa05Dk/bcT4DykvePiVLDjjEy2zbu
		HTTP/1.0 204 NO CONTENT
		Content-Encoding: gzip
		Content-Length: 0
		Content-Type: application/json
		Date: Thu, 19 Feb 2015 12:20:50 GMT
		Server: Werkzeug/0.10.1 Python/2.7.3
		Vary: Accept-Encoding

	Verify:

	.. code-block:: javascript

		$ http --verify=no https://localhost:7789/v1/keys Authorization:"Basic \$2a\$12\$xVOCuxixOd9ly/xiUlWqg.7mIa05Dk/bcT4DykvePiVLDjjEy2zbu"
		HTTP/1.0 401 UNAUTHORIZED
		Content-Length: 38
		Content-Type: application/json
		Date: Thu, 19 Feb 2015 12:20:55 GMT
		Server: Werkzeug/0.10.1 Python/2.7.3
		WWW-Authenticate: Basic realm="flask-restful"

		{
		    "message": "Invalid API Key."
		}

