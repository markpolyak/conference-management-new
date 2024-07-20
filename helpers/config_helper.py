import os
from yaml import load, Loader


def get_config():
    appdata_path = os.environ.get('APPDATA')

    config_path = os.path.join(appdata_path, 'conferences', 'config.yml')

    with open(config_path, 'r') as f:
        config = load(f, Loader=Loader)

    return config

