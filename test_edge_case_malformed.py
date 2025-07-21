import os


def test_malformed_syntax():
    # This function has intentional syntax that might confuse parsers
    os.system("echo test")  # This should still be detected
    
    # Incomplete string - but this file should still scan successfully