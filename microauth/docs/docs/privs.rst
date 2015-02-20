Privs
=====================================
Privileges behavior is defined by the application developer. Microauth will simply tell you whether a user has access to them.
This permits single privileges to have numerous behaviors; Limited only by your imagination.

Creating
-----------------
To create privileges in bulk you can make a **PUT** request to the **/v1/privs** endpoint specifying a comma-separated list of names in the **name** field of the request body.

An optional argument is **systemwide** which will put the new privileges in the global namespace presuming there's no pre-existing ones that could be overwritten.

.. code-block:: javascript

	$ http --verify=no PUT https://localhost:7789/v1/privs Authorization:"Basic \$2a\$12\$xVOCuxixOd9ly/xiUlWqg.7mIa05Dk/bcT4DykvePiVLDjjEy2zbu" name=Create,Read,Write,Append,Delete
	HTTP/1.0 201 CREATED
	Content-Length: 809
	Content-Type: application/json
	Date: Thu, 19 Feb 2015 13:14:45 GMT
	Server: Werkzeug/0.10.1 Python/2.7.3

	[
	    {
	        "created": "Thursday, 19. February 2015 01:14PM", 
	        "name": "Create", 
	        "parent_key": "SomeApp", 
	        "systemwide": false
	    }, 
	    {
	        "created": "Thursday, 19. February 2015 01:14PM", 
	        "name": "Read", 
	        "parent_key": "SomeApp", 
	        "systemwide": false
	    }, 
	    {
	        "created": "Thursday, 19. February 2015 01:14PM", 
	        "name": "Write", 
	        "parent_key": "SomeApp", 
	        "systemwide": false
	    }, 
	    {
	        "created": "Thursday, 19. February 2015 01:14PM", 
	        "name": "Append", 
	        "parent_key": "SomeApp", 
	        "systemwide": false
	    }, 
	    {
	        "created": "Thursday, 19. February 2015 01:14PM", 
	        "name": "Delete", 
	        "parent_key": "SomeApp", 
	        "systemwide": false
	    }
	]

Consuming
-----------------

.. http:get:: /v1/privs/(privilege)

	Individually:

	.. code-block:: javascript

		$ http --verify=no https://localhost:7789/v1/privs/Create Authorization:"Basic \$2a\$12\$xVOCuxixOd9ly/xiUlWqg.7mIa05Dk/bcT4DykvePiVLDjjEy2zbu"
		HTTP/1.0 200 OK
		Content-Length: 136
		Content-Type: application/json
		Date: Thu, 19 Feb 2015 13:29:03 GMT
		Server: Werkzeug/0.10.1 Python/2.7.3

		{
		    "created": "Thursday, 19. February 2015 01:14PM", 
		    "name": "Create", 
		    "parent_key": "SomeApp", 
		    "systemwide": false
		}


.. http:get:: /v1/privs

	In bulk:

	.. code-block:: javascript

		$ http --verify=no https://localhost:7789/v1/privs Authorization:"Basic \$2a\$12\$xVOCuxixOd9ly/xiUlWqg.7mIa05Dk/bcT4DykvePiVLDjjEy2zbu"
		HTTP/1.0 200 OK
		Content-Encoding: gzip
		Content-Length: 165
		Content-Type: application/json
		Date: Thu, 19 Feb 2015 13:31:13 GMT
		Server: Werkzeug/0.10.1 Python/2.7.3
		Vary: Accept-Encoding

		[
		    {
		        "created": "Thursday, 19. February 2015 01:14PM", 
		        "name": "Create", 
		        "parent_key": "SomeApp", 
		        "systemwide": false
		    }, 
		    {
		        "created": "Thursday, 19. February 2015 01:14PM", 
		        "name": "Read", 
		        "parent_key": "SomeApp", 
		        "systemwide": false
		    }, 
		    { ...
		    }
		]

	Bulk responses can be paginated using **?page=#** where **#** is an integer. This defaults to 50 items per response and can be altered with the **per_page** parameter.

	.. code-block:: javascript

		$ http --verify=no https://localhost:7789/v1/privs?page=1\&per_page=2  Authorization:"Basic \$2a\$12\$xVOCuxixOd9ly/xiUlWqg.7mIa05Dk/bcT4DykvePiVLDjjEy2zbu"
		HTTP/1.0 200 OK
		Content-Encoding: gzip
		Content-Length: 145
		Content-Type: application/json
		Date: Thu, 19 Feb 2015 15:03:23 GMT
		Server: Werkzeug/0.10.1 Python/2.7.3
		Vary: Accept-Encoding

		[
		    {
		        "created": "Thursday, 19. February 2015 01:14PM", 
		        "name": "Create", 
		        "parent_key": "SomeApp", 
		        "systemwide": false
		    }, 
		    {
		        "created": "Thursday, 19. February 2015 01:14PM", 
		        "name": "Read", 
		        "parent_key": "SomeApp", 
		        "systemwide": false
		    }
		]

Modifying
-----------------
To place these into the global namespace from a systemwide key:

.. code-block:: javascript

	$ http --verify=no POST https://localhost:7789/v1/privs Authorization:"Basic \$2a\$12\$xVOCuxixOd9ly/xiUlWqg.7mIa05Dk/bcT4DykvePiVLDjjEy2zbu" name=Create,Read,Write,Append,Delete systemwide=1
	HTTP/1.0 200 OK
	Content-Length: 634
	Content-Type: application/json
	Date: Thu, 19 Feb 2015 13:23:53 GMT
	Server: Werkzeug/0.10.1 Python/2.7.3

	[
	    {
	        "created": "Thursday, 19. February 2015 01:14PM", 
	        "name": "Create", 
	        "systemwide": true
	    }, 
	    {
	        "created": "Thursday, 19. February 2015 01:14PM", 
	        "name": "Read", 
	        "systemwide": true
	    }, 
	    {
	        "created": "Thursday, 19. February 2015 01:14PM", 
    	    "name": "Write", 
	        "systemwide": true
	    }, 
	    {
    	    "created": "Thursday, 19. February 2015 01:14PM", 
	        "name": "Append", 
	        "systemwide": true
		    }, 
	    {
	        "created": "Thursday, 19. February 2015 01:14PM", 
	        "name": "Delete", 
	        "systemwide": true
	    }
	]

To reverse this you will need to have **global_delete** enabled on your key as you would be removing the privileges from other applications.

Deleting
-----------------

.. http:delete:: /v1/privs

	A comma-separated list can be used in the **name** field of the request body.

	.. code-block:: javascript

		$ http --verify=no delete https://localhost:7789/v1/privs Authorization:"Basic \$2a\$12\$xVOCuxixOd9ly/xiUlWqg.7mIa05Dk/bcT4DykvePiVLDjjEy2zbu" name=Append,Delete
		HTTP/1.0 204 NO CONTENT
		Content-Length: 0
		Content-Type: application/json
		Date: Thu, 19 Feb 2015 13:35:04 GMT
		Server: Werkzeug/0.10.1 Python/2.7.3
