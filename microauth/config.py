import os
if not 'MICROAUTH_DATABASE' in os.environ:
#	print 'You need to export a path for MICROAUTH_DATABASE'
#	print 'Eg: export MICROAUTH_DATABASE = "sqlite://///home/you/.microauth.db"'
	SQLALCHEMY_DATABASE_URI = (
    	"sqlite:///:memory:"
	)
else:
	SQLALCHEMY_DATABASE_URI = (
    	os.environ['MICROAUTH_DATABASE']
	)

MASTER_KEY = None
MASTER_KEY_NAME = "Master"
PERMIT_NEW = True
BCRYPT_ROUNDS = 12
GZIP_HERE = True
