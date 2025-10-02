from parser import parser_flow
from metaflow import Runner
import yaml

def read_config_file(configfile):
        """
        Reads the YAML configuration file
        """
        config = None
        try:
            with open(configfile, 'r') as source:
                config = yaml.safe_load(source)
        except (IOError, TypeError, yaml.YAMLError) as e:
            print(f"Error reading config file: {e}")
        return config


if __name__ == "__main__":

    with Runner('parser.py', show_output=False).run() as running:
        if running.status == 'failed':
            print(f'❌ {running.run} failed:')
        elif running.status == 'successful':
            print(f'✅ {running.run} succeeded:')
        print(f'-- stdout --\n{running.stdout}')
        print(f'-- stderr --\n{running.stderr}')

    # Runner(parser_flow()).run()
