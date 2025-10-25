import environ
import os

def get_secret_var(var_name):

    project_root = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(project_root)

    env = environ.Env(DEBUG=(bool, True))

    # Prefer .env at project root; fallback to parent dir for backward compatibility
    candidates = [
        os.path.join(project_root, ".env"),
        os.path.join(parent_dir, ".env"),
    ]

    for env_file in candidates:
        if os.path.exists(env_file):
            env.read_env(env_file)
            break

    return env(var_name)