pyvenv ~/microauth
source ~/microauth/bin/activate
curl https://raw.githubusercontent.com/pypa/pip/master/contrib/get-pip.py | python
deactivate
source ~/microauth/bin/activate

pip install --editable /vagrant
python3 /vagrant/scripts/create_db.py
