import os
from typing import Dict


def load_env(path: str = ".env") -> Dict[str, str]:
    """Load environment variables from a .env file.

    Parameters
    ----------
    path: str
        Path to the .env file.

    Returns
    -------
    Dict[str, str]
        Dictionary of environment variables loaded from the file.
    """
    env_vars: Dict[str, str] = {}
    if not os.path.exists(path):
        return env_vars

    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            env_vars[key] = value
            os.environ.setdefault(key, value)

    return env_vars
