import os

# This file should be EXCLUDED from scanning due to being in tests directory
def test_something_insecure():
    os.system("rm -rf /")  # This should NOT be detected if exclusion works