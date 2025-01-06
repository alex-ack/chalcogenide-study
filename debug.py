import sys
import os
import subprocess

print("\n🔍 DEBUGGING PYTHON ENVIRONMENT\n")

# 1. Python version
print("1. Python Version:")
print(sys.version)
print()

# 2. Python executable path
print("2. Python Executable Path:")
print(sys.executable)
print()

# 3. Environment variables
print("3. PYTHONPATH Environment Variable:")
print(os.environ.get('PYTHONPATH', 'Not Set'))
print()

# 4. Installed packages
print("4. Installed 'mp-api' Package:")
try:
    import mp_api
    print("mp-api is installed.")
    print("mp-api version:", mp_api.__version__)
except ImportError as e:
    print("ImportError:", str(e))
print()

# 5. Test import
print("5. Test Import for 'MPRester':")
try:
    from mp_api.client import MPRester
    print("MPRester import successful!")
except ImportError as e:
    print("ImportError:", str(e))
print()

# 6. Site-packages path
print("6. Site-Packages Paths:")
for path in sys.path:
    print(path)
print()

# 7. PIP Environment Check
print("7. PIP Environment:")
try:
    result = subprocess.run(["pip", "show", "mp-api"], capture_output=True, text=True)
    print(result.stdout)
except Exception as e:
    print("Error running pip:", str(e))
print()

# 8. Active Virtual Environment
print("8. Active Virtual Environment:")
venv = os.environ.get('VIRTUAL_ENV', 'None')
print("Virtual Env:", venv)
print()

print("\n✅ DEBUGGING COMPLETE!")
# source chalco_env/bin/activate