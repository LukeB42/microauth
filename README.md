# Microauth

Microauth is an authentication and authorization microservice that aims to make
setting up a secure authentication flow as simple as possible.

Microauth exposes a simple to use REST API for registering, updating and
authenticating users.
Important details like proper password hashing are taken care of for you.

Microauth also supports authorization using role-based privileges, and key-based
authentication.

To install Microauth simply run `sudo python setup.py install`

Once installed, try `python -m microauth.run --help` for help on running the service.

An interactive interpreter can be started with `python -m microauth.repl`.

Documentation is available to read by navigating to `docs/_build/html`, running
`python -m SimpleHTTPServer` and visiting `localhost:8000/index.html` in your browser.
