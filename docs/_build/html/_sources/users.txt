Users
=====================================
Microauth presents simple facilities for authenticating users, leaving it up to the application developer how sessions are managed.

Creating users
-----------------
.. http:put:: /v1/user

	To create a new user simply define the following parameters in the request body:

	* **username**
	* **name**
	* **email**
	* **password**
	* An optional parameter **systemwide** can create global users directly.

	.. code-block:: javascript

		$ http --verify=no put https://localhost:7789/v1/users Authorization:"Basic \$2a\$12\$xVOCuxixOd9ly/xiUlWqg.7mIa05Dk/bcT4DykvePiVLDjjEy2zbu" username="SomeUser" name="John Doe" email="SomeUser@somehost.tld" password="SomePass"
		HTTP/1.0 201 CREATED
		Content-Encoding: gzip
		Content-Length: 148
		Content-Type: application/json
		Date: Thu, 19 Feb 2015 12:36:44 GMT
		Server: Werkzeug/0.10.1 Python/2.7.3
		Vary: Accept-Encoding

		{
		    "created": "Thursday, 19. February 2015 12:36PM", 
		    "email": "SomeUser@somehost.tld", 
		    "name": "John Doe", 
		    "systemwide": false, 
		    "username": "SomeUser"
		}

Authentication
-----------------
.. http:get:: /v1/user/(username)/login

	.. raw:: html

		Authenticating is a simple as making a get request to <strong>/v1/users/</strong><em>username</em><strong>/login</strong>?password=<em>password</em>

	.. code-block:: javascript

		$ http --verify=no https://localhost:7789/v1/users/SomeUser/login?password=SomePass Authorization:"Basic \$2a\$12\$xVOCuxixOd9ly/xiUlWqg.7mIa05Dk/bcT4DykvePiVLDjjEy2zbu"
		HTTP/1.0 200 OK
		Content-Length: 23
		Content-Type: application/json
		Date: Thu, 19 Feb 2015 12:43:07 GMT
		Server: Werkzeug/0.10.1 Python/2.7.3

		true

	.. raw:: html

		An incorrect password would result in <span class="apikey">false</span>.<br /><br />


		To avoid sending passwords as a URL parameter it is possible to authenticate with a <strong>POST</strong> request to the <strong>/users/</strong>username<strong>/login</strong> endpoint with a <strong>password</strong> field in the request body.<br />
		It's not RESTful in that you're not updating a resource but it keeps passwords out of terminal memory.

Key files
^^^^^^^^^^^^^^^^^
Microauth can also verify authentication through file uploads. This may be useful if you would like to validate access to resources through
peripherals like card readers or unique strings stegenographically embedded in cat macros.

.. raw:: html

	To set a key file simply make a <strong>POST</strong> request to <strong>/v1/users/</strong><em>username</em>


.. code-block:: javascript

	$ curl -k --header "Authorization:Basic \$2a\$12\$xVOCuxixOd9ly/xiUlWqg.7mIa05Dk/bcT4DykvePiVLDjjEy2zbu" -i -F "keyfile=@./keyfile" https://localhost:7789/v1/users/SomeUser
	HTTP/1.1 100 Continue

	HTTP/1.0 200 OK
	Content-Type: application/json
	Content-Length: 36
	Server: Werkzeug/0.10.1 Python/2.7.3
	Date: Thu, 19 Feb 2015 13:01:14 GMT

	{
	    "message": "User modified."
	}

.. raw:: html

	and to verify, make the same request to <strong>/v1/users/</strong><em>username</em><strong>/login</strong>:

.. code-block:: javascript

	$ curl -k --header "Authorization:Basic \$2a\$12\$xVOCuxixOd9ly/xiUlWqg.7mIa05Dk/bcT4DykvePiVLDjjEy2zbu" -i -F "keyfile=@./keyfile" https://localhost:7789/v1/users/SomeUser/login
	HTTP/1.1 100 Continue

	HTTP/1.0 200 OK
	Content-Type: application/json
	Content-Length: 5
	Server: Werkzeug/0.10.1 Python/2.7.3
	Date: Thu, 19 Feb 2015 13:03:33 GMT

	true

Authorisation
-----------------
.. http:get:: /v1/user/(username)?can=(privilege)

	To determine whether a user has a privilege you can issue this simple request:

	.. code-block:: javascript

		$ http --verify=no https://localhost:7789/v1/users/SomeUser?can=Write Authorization:"Basic \$2a\$12\$xVOCuxixOd9ly/xiUlWqg.7mIa05Dk/bcT4DykvePiVLDjjEy2zbu"
		HTTP/1.0 200 OK
		Content-Length: 5
		Content-Type: application/json
		Date: Thu, 19 Feb 2015 15:34:23 GMT
		Server: Werkzeug/0.10.1 Python/2.7.3

		true

	.. raw:: html

		<span class="apikey">null</span> would mean the privilege wasn't available through any associated roles.

Deleting
-----------------
.. http:delete:: /v1/users/(username)

	.. raw:: html

		Deleting users is as simple as sending a <strong>DELETE</strong> request to the <strong>/users/</strong><em>username</em> endpoint.
