#!/usr/bin/env python
import sys
sys.path.insert(0, r'c:\Users\WELCOME\Downloads\seagrass\seagrass\source code\seagrass\seagrass\virtualenv\Lib\site-packages')

print("Testing PyMySQL installation...")
try:
    import pymysql
    print(f"✓ PyMySQL imported successfully (version {pymysql.__version__})")
    
    # Try to patch
    pymysql.install_as_MySQLdb()
    print("✓ PyMySQL patch applied")
    
    # Try importing as MySQLdb
    sys.modules['MySQLdb'] = pymysql
    import MySQLdb
    print("✓ MySQLdb alias created and imported")
    
    print("\nNow testing Django...")
    import os
    os.environ['DJANGO_SETTINGS_MODULE'] = 'seagrass_project.settings'
    
    # Add project to path
    sys.path.insert(0, r'c:\Users\WELCOME\Downloads\seagrass\seagrass\source code\seagrass\seagrass')
    
    import django
    django.setup()
    print("✓ Django setup successful!")
    
except Exception as e:
    import traceback
    print(f"✗ Error: {e}")
    traceback.print_exc()
