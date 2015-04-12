Events
=====================================

Microauth keeps a log of all authentication attempts for playback at your leisure. They look like this:

.. http:get:: /v1/events/(username)

	.. code-block:: javascript

		> get events/LukeB42
		200
		[
		    {
		        "username": "LukeB42",
		        "success": true,
		        "key": "Wiki",
		        "time": "Thursday, 19. March 2015 09:42AM"
		    }
		]

Application log
-----------------

You can review the events for your application at the **/events** endpoint, like so:


.. http:get:: /v1/events?page=X&per_page=Y

	.. code-block:: javascript

		> get events?page=1&per_page=2
		200
		[
		    {
		        "username": "Test", 
		        "success": false, 
		        "id": "TY2MjY2MTU0MQ", 
		        "key": "Wiki", 
		        "time": "Thursday, 19. March 2015 10:31AM"
		    }, 
		    {
		        "username": "Test", 
		        "success": true, 
		        "id": "TY2MjY2MTU0MQ", 
		        "key": "Wiki", 
		        "time": "Thursday, 19. March 2015 10:31AM"
		    }
		]

