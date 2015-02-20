Administration
=====================================

Microauth works by parenting objects (*Users*, *Roles* and *Privileges*) to API Keys.
Objects that are not parented to an API key are considered global to the system.
Keys can be switched into systemwide mode, giving them access to these objects.

A simple REST interface is presented at **/keys**, **/users**, **/roles** and **/privs**, using PUT to create, POST to modify,
DELETE to.. and GET to verify/examine. 

This documentation is only concerned with the API revealed on the **/v1** prefix. (**/v1/users** etc)

Getting started
-----------------
Reviewing your ./microauth/config.py it should look something like this...

.. code-block:: python

    SQLALCHEMY_DATABASE_URI = ("sqlite:///microauth")
    MASTER_KEY_NAME = "Master"
    PERMIT_NEW = True # Permit strangers to generate API keys for themselves.
    BCRYPT_ROUNDS = 12
    GZIP_HERE = True  # Apply compression in this application (instead of in nginx or something)

.. warning::

	.. raw:: html

		Redefining <strong>MASTER_KEY_NAME</strong> during operation can change which key is treated as the master.<br />
		Please secure the file permissions on your <em>config.py</em>. (<em>chmod 600 config.py</em> if in doubt)

When you start Microauth for the first time the database will be populated with a schema and the first API Key will be introduced,
with the name defined in config.py as **MASTER_KEY_NAME**. Eg:

.. raw:: html

    <blockquote>
    ./run.py --key key --cert cert<br />
    <span class="apikey">$2a$12$P6py8egFp35kyCsA10DRtuniD8WwRQOGBv27ZLRqKbDUkvBR7J8XW</span><br />
     * Running on http://0.0.0.0:7789/ (Press CTRL+C to quit)<br />
     * Restarting with stat<br />
    </blockquote><br />

This key can be used to determine whether new keys can be created or to simply review the system. For instance, using `httpie`_:

.. _httpie: https://github.com/jakubroztocil/httpie


.. http:get:: /v1/keys

	.. code-block:: javascript

		$ http --verify=no localhost:7789/v1/keys "Authorization: Basic \$2a\$12\$R0yq8EOnxgWTuIuEPwwbsusQ8qgLTYSpUhpuhJjbw0mDHJZN9ERZm"
		HTTP/1.0 200 OK
		Content-Encoding: gzip
		Content-Length: 170
		Content-Type: application/json
		Date: Wed, 18 Feb 2015 15:39:26 GMT
		Server: Werkzeug/0.10.1 Python/2.7.3
		Vary: Accept-Encoding
	
		[   
		    {   
		        "active": true,
		        "global_delete": true,
		        "name": "Master",
		        "privileges": [],
		        "roles": [],
		        "system": {
		            "keys": [
		                "Master"
		            ],
		            "permit_new": true,
		            "privileges": [],
		            "roles": [],
		            "users": []
		        },
		        "systemwide": true,
		        "users": []
		    }
		]

.. note::
    Dollar signs in the key need to be escaped on the command line.

Your first key
-----------------
A new (ordinary) key can be obtained by making a **PUT** request specifying the name of your new program:

.. http:put:: /v1/keys

	.. code-block:: javascript

		$ http --verify=no put https://localhost:7789/v1/keys name=NewApp
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

Notice that no API Key was required to grant this. This aspect can be determined by using the master key to toggle **permit_new**.

.. http:post:: /v1/keys

	.. code-block:: javascript

		$ http --verify=no post https://localhost:7789/v1/keys Authorization:"Basic \$2a\$12\$R0yq8EOnxgWTuIuEPwwbsusQ8qgLTYSpUhpuhJjbw0mDHJZN9ERZm" permit_new=
		HTTP/1.0 200 OK
		Content-Encoding: gzip
		Content-Length: 62
		Content-Type: application/json
		Date: Thu, 19 Feb 2015 11:24:08 GMT
		Server: Werkzeug/0.10.1 Python/2.7.3
		Vary: Accept-Encoding

		{
		    "system": {
		        "permit_new": false
		    }
		}

Subsequent new keys would have to be produced by requests made by the master key.
See the section on :doc:`keys` for more information on managing and listing keys.
