# Patch PyMySQL as MySQLdb before importing Django's MySQL backend
try:
    import pymysql
    pymysql.install_as_MySQLdb()
except (ImportError, AttributeError):
    pass

# Now import everything from the standard Django MySQL backend
from django.db.backends.mysql.base import *  # noqa
from django.db.backends.mysql.base import DatabaseWrapper  # noqa: F401
