import yaml

# this file read the yaml configuration file and provide three methods to retrieve configuration module
with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)


def smtp_config():
    return config["smtp"]


def server_config():
    return config["server"]


def database_config():
    return config["database"]
