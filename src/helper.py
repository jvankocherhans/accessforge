import os
from dotenv import load_dotenv

# Load the .env file
load_dotenv()

def get_env_variable(key, default=None):
    """
    Get the value of an environment variable from .env or system environment.
    If the variable is not found, return the default value.
    """
    return os.getenv(key, default)
