# Use PyMySQL as MySQLdb to avoid AppLocker DLL blocks
try:
    import pymysql
    pymysql.install_as_MySQLdb()
except (ImportError, AttributeError):
    pass
