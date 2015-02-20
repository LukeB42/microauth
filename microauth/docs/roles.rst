Roles
=====================================
Roles are how privileges attach to users.
Roles can have multiple privileges and multiple users, with these privileges being set to either *allow* or *deny*.

Creating
-----------------

.. http:put:: /v1/roles

	Roles can be created by specifying a comma-separated list of roles in the **name** field in the request body of a **PUT** request to **/v1/roles**

	An optional **systemwide** field can be used to put these roles into the global namespace upon creation.

	.. code-block:: javascript

		 $ http --verify=no put https://localhost:7789/v1/roles  Authorization:"Basic \$2a\$12\$xVOCuxixOd9ly/xiUlWqg.7mIa05Dk/bcT4DykvePiVLDjjEy2zbu" name=Administrators,Moderators,Users,Anonymous,Customers,Staff,Mobile
		HTTP/1.0 201 CREATED
		Content-Encoding: gzip
		Content-Length: 192
		Content-Type: application/json
		Date: Thu, 19 Feb 2015 15:07:35 GMT
		Server: Werkzeug/0.10.1 Python/2.7.3
		Vary: Accept-Encoding

		[
		    {
		        "created": "Thursday, 19. February 2015 03:07PM", 
		        "name": "Administrators", 
		        "parent_key": "SomeApp", 
		        "systemwide": false
		    }, 
		    {
		        "created": "Thursday, 19. February 2015 03:07PM", 
		        "name": "Moderators", 
		        "parent_key": "SomeApp", 
		        "systemwide": false
		    }, 
		    {
		        "created": "Thursday, 19. February 2015 03:07PM", 
		        "name": "Users", 
		        "parent_key": "SomeApp", 
		        "systemwide": false
		    }, 
		    {
		        "created": "Thursday, 19. February 2015 03:07PM", 
		        "name": "Anonymous", 
		        "parent_key": "SomeApp", 
		        "systemwide": false
		    }, 
		    {
		        "created": "Thursday, 19. February 2015 03:07PM", 
		        "name": "Customers", 
		        "parent_key": "SomeApp", 
		        "systemwide": false
		    }, 
		    {
		        "created": "Thursday, 19. February 2015 03:07PM", 
		        "name": "Staff", 
		        "parent_key": "SomeApp", 
		        "systemwide": false
		    }, 
		    {
		        "created": "Thursday, 19. February 2015 03:07PM", 
		        "name": "Mobile", 
		        "parent_key": "SomeApp", 
		        "systemwide": false
		    }
		]


Consuming
-----------------

.. http:put:: /v1/roles

	Data on roles available to your API key can be consumed all at once or in chunks by specifying **page=** and **per_page=**
	
	The default value for **per_page** is 50.

	.. code-block:: javascript

		$ http --verify=no https://localhost:7789/v1/roles?page=1\&per_page=3  Authorization:"Basic \$2a\$12\$xVOCuxixOd9ly/xiUlWqg.7mIa05Dk/bcT4DykvePiVLDjjEy2zbu"
		HTTP/1.0 200 OK
		Content-Encoding: gzip
		Content-Length: 161
		Content-Type: application/json
		Date: Thu, 19 Feb 2015 15:11:46 GMT
		Server: Werkzeug/0.10.1 Python/2.7.3
		Vary: Accept-Encoding

		[
		    {
		        "created": "Thursday, 19. February 2015 03:07PM", 
		        "name": "Administrators", 
		        "parent_key": "SomeApp", 
		        "systemwide": false
		    }, 
		    {
		        "created": "Thursday, 19. February 2015 03:07PM", 
		        "name": "Moderators", 
		        "parent_key": "SomeApp", 
		        "systemwide": false
		    }, 
		    {
		        "created": "Thursday, 19. February 2015 03:07PM", 
		        "name": "Users", 
		        "parent_key": "SomeApp", 
		        "systemwide": false
		    }
		]

	.. raw:: html

		Individual roles can be examined through <strong>/v1/roles/</strong><em>name</em>

	.. code-block:: javascript

		$ http --verify=no https://localhost:7789/v1/roles/Administrators Authorization:"Basic \$2a\$12\$xVOCuxixOd9ly/xiUlWqg.7mIa05Dk/bcT4DykvePiVLDjjEy2zbu"
		HTTP/1.0 200 OK
		Content-Encoding: gzip
		Content-Length: 156
		Content-Type: application/json
		Date: Thu, 19 Feb 2015 15:16:09 GMT
		Server: Werkzeug/0.10.1 Python/2.7.3
		Vary: Accept-Encoding

		{
		    "created": "Thursday, 19. February 2015 03:07PM", 
		    "name": "Administrators", 
		    "parent_key": "SomeApp", 
		    "privileges": [], 
		    "systemwide": false, 
		    "users": []
		}




Modifying
-----------------
Roles can be modified into and out of the global namespace en-masse with a **POST** request to the **/v1/roles** endpoint

.. http:post:: /v1/roles

    .. code-block:: javascript

        $ http --verify=no post https://127.0.0.1:7789/v1/roles Authorization:"Basic \$2a\$12\$0Yd5C3FWsTlc/SC8WIEGDuVoakU0fEWop81XQSWUOCyOHIP0zJ..q" name=Subscribers,Writers systemwide=1
        HTTP/1.0 200 OK
        Content-Length: 262
        Content-Type: application/json
        Date: Fri, 20 Feb 2015 14:30:02 GMT
        Server: Werkzeug/0.10.1 Python/2.7.3

        [   
            {   
                "created": "Thursday, 19. February 2015 08:50AM",
                "name": "Subscribers",
                "systemwide": true
            },
            {   
                "created": "Thursday, 19. February 2015 08:50AM",
                "name": "Writers",
                "systemwide": true
            }
        ]

The roles endpoint is useful in that an individual role can be modified into its ultimately desired state in one call.

.. http:post:: /v1/roles/(name)


	To demonstrate let's quickly add some privs:

	.. code-block:: javascript

		$ http --verify=no post  https://localhost:7789/v1/roles/Users Authorization:"Basic \$2a\$12\$xVOCuxixOd9ly/xiUlWqg.7mIa05Dk/bcT4DykvePiVLDjjEy2zbu" allow=Create,Read
		HTTP/1.0 200 OK
		Content-Length: 119
		Content-Type: application/json
		Date: Thu, 19 Feb 2015 15:21:02 GMT
		Server: Werkzeug/0.10.1 Python/2.7.3

		{
		    "allow": [
		        {
		            "Create": true
		        }, 
		        {
		            "Read": true
		        }
		    ]
		}

	And now we will allow, revoke and deny privs while adding the role to a user:

	.. code-block:: javascript

		$ http --verify=no post  https://localhost:7789/v1/roles/Users Authorization:"Basic \$2a\$12\$xVOCuxixOd9ly/xiUlWqg.7mIa05Dk/bcT4DykvePiVLDjjEy2zbu" allow=Write deny=Create revoke=Read add=SomeUser
		HTTP/1.0 200 OK
		Content-Length: 250
		Content-Type: application/json
		Date: Thu, 19 Feb 2015 15:21:35 GMT
		Server: Werkzeug/0.10.1 Python/2.7.3

		{
		    "add": [
		        "SomeUser"
		    ], 
		    "allow": [
		        {
		            "Write": true
		        }
		    ], 
		    "deny": [
		        {
		            "Create": false
		        }
		    ], 
		    "revoke": [
		        {
		            "Read": true
		        }
		    ]
		}

	Let's verify that *SomeUser* can *Write*:

	.. code-block:: javascript

		$ http --verify=no https://localhost:7789/v1/users/SomeUser?can=Write Authorization:"Basic \$2a\$12\$xVOCuxixOd9ly/xiUlWqg.7mIa05Dk/bcT4DykvePiVLDjjEy2zbu"
		HTTP/1.0 200 OK
		Content-Length: 5
		Content-Type: application/json
		Date: Thu, 19 Feb 2015 15:25:42 GMT
		Server: Werkzeug/0.10.1 Python/2.7.3

		true

Deleting
-----------------

.. http:delete:: /v1/roles

	Use a comma-separated list of names in the **name** field of the request body to delete roles in bulk.

	.. code-block:: javascript

		$ http --verify=no delete https://localhost:7789/v1/roles Authorization:"Basic \$2a\$12\$xVOCuxixOd9ly/xiUlWqg.7mIa05Dk/bcT4DykvePiVLDjjEy2zbu" name=Anonymous,Moderators
		HTTP/1.0 204 NO CONTENT
		Content-Encoding: gzip
		Content-Length: 0
		Content-Type: application/json
		Date: Thu, 19 Feb 2015 15:28:14 GMT
		Server: Werkzeug/0.10.1 Python/2.7.3
		Vary: Accept-Encoding

