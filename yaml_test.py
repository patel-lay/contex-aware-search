import yaml

class ConfigReader:
    def __init__(self, configfile):
        self.configfile = configfile

    def read_config_file(self):
        try:
            with open(self.configfile, 'r') as source:
                return yaml.safe_load(source)
        except (IOError, TypeError, yaml.YAMLError) as e:
            print(f"Error reading config file: {e}")
            return None

# Usage
config_reader = ConfigReader("config.yml")
config = config_reader.read_config_file()

sources = config.get("sources", [])

# Extract into variables
web_sources = [src for src in sources if src.get("type") == "web"]
markdown_sources = [src for src in sources if src.get("type") == "markdown"]

# Example: store URLs, depths, and paths separately
web_urls = [src["url"] for src in web_sources]
web_depths = [src["depth"] for src in web_sources]
markdown_paths = [src["path"] for src in markdown_sources]

# Print results
print("Web URLs:", web_urls)
print("Web Depths:", web_depths)
print("Markdown Paths:", markdown_paths)
