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


