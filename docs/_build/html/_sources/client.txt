Client
=====================================

A simple REPL program is included as part of the Microauth installation and can help demonstrate how to use the client library.
As of writing, the client library is only 80 lines in length, so you may benefit from giving it a quick review, especially during application development.
This section will demonstrate things like signing in, checking privileges and changing passwords, first from the interactive interpreter.

On startup it will read the environment for the location of your database and default to using the master key.

.. raw:: html

	<blockquote>python -m microauth.repl<br />
	&gt; getkey<br />
    <span class="apikey">$2a$12$P6py8egFp35kyCsA10DRtuniD8WwRQOGBv27ZLRqKbDUkvBR7J8XW</span><br />
	&gt;</blockquote><br />
	An optional <em>--host</em> argument is available in the form of <em>hostname</em>:<em>port</em>/<em>v1</em>/

The key can be changed with **setkey** or **use**, which is an alias for setkey. Especially useful for interacting with remote Microauth instances.

.. code-block:: javascript

	> get keys/Wiki
	200
	{
	    "systemwide": null,
	    "apikey": "$2a$12$pa4PfOB.fYzdhjinNMDtaOTZgqcMXHI0OUQcpwKM5VDf13hKX.3vC",
	    "name": "Wiki",
	[ ... ]
	
	> use $2a$12$pa4PfOB.fYzdhjinNMDtaOTZgqcMXHI0OUQcpwKM5VDf13hKX.3vC
	Changed active API key to "$2a$12$pa4PfOB.fYzdhjinNMDtaOTZgqcMXHI0OUQcpwKM5VDf13hKX.3vC"
	>


From here, anything you would normally do with the REST api can be done with the commands in the interpreter.

For instance let's modify the *Writers* role for a wiki, by appending a handful of privileges to this group.

.. code-block:: javascript

	> get roles/Writers
	200
	{
	    "systemwide": false, 
	    "name": "Writers", 
	    "parent_key": "Wiki", 
	    "created": "Tuesday, 24. February 2015 11:13AM", 
    	"privileges": [], 
		    "users": []
	}
	
	> post roles/Writers allow=read,write,delete,pagegroup
	200
	{
	    "allow": [
	        {
    	        "read": true
		        }, 
	        {
    	        "write": true
		        }, 
	        {
    	        "delete": true
		        }, 
	        {
	    	        "pagegroup": true
	        }
	    ]
	}

	> 

Notice the format of the **post** command. The REPL currently doesn't support arguments with spaces in them. Fortunately, Microauth recognises comma-separated lists.
