import environ
import os

def get_secret_var(var_name):

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


    env = environ.Env(DEBUG=(bool, True))
    env_file = os.path.join(BASE_DIR, ".env")
    env.read_env(env_file)


    return env(var_name)