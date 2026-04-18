# Custom MySQL backend that uses PyMySQL instead of mysqlclient

# Patch PyMySQL as MySQLdb before importing Django's MySQL backend
try:
    import pymysql
    pymysql.install_as_MySQLdb()
except (ImportError, AttributeError):
    pass

# Now import the standard Django MySQL backend
from django.db.backends.mysql import *
