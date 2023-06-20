import os
import yaml


class CoreConfigurator:
    def __init__(self, yaml_config="config.yaml"):
        self.cp2_url = None
        if os.path.exists(yaml_config):
            self._load_config_from_yaml_file(yaml_config)

    def _load_config_from_yaml_file(self, config_file):
        with open(config_file) as config_file:

            config: dict = yaml.safe_load(config_file)
            self.API_KEY = config.get("API_KEY")
            self.ids = config.get("ids")


core_configurator = CoreConfigurator()
