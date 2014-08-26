# Microauth

Microauth is an authentication microservice that aims to make setting up a
secure authentication flow as simple as possible.

Microauth exposes a simple to use REST API for registering, updating and
authenticating users. Important details like proper password hashing are taken
care of for you.

Microauth is under development and should not be used in production for the
time being. If you are interested in hacking on Microauth, setting up a
development environment is simple. Simply get Vagrant installed and run

    $ vagrant up

The development environment exposes the service on `localhost:5000`.