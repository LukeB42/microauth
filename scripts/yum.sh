#!/usr/bin/env bash

yum install libffi-devel python3 python3-devel postgresql-server postgresql-devel -y

systemctl enable postgresql
postgresql-setup initdb
systemctl start postgresql
su postgres -c "psql -d postgres -c $'create user vagrant with password \'vagrant\';'"
su postgres -c "createdb --owner=vagrant microauth"
