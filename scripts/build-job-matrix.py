import json
import os
import sys
from itertools import product

DEFAULT_CONFIG_PATH = 'opensciencegrid/default-build-config.json'


def load_config(config_path, default_config=None):
    """Load JSON configuration from the given path."""
    try:
        with open(config_path, 'r') as file:
            config = json.load(file)
            if not config and default_config is not None:
                return default_config
            return config
    except (FileNotFoundError, json.JSONDecodeError):
        if default_config is not None:
            return default_config
        else:
            raise


def main(image_dirs):
    print("Image directories:", image_dirs)

    default_config = load_config(DEFAULT_CONFIG_PATH)

    include_list = []

    for image_dir in image_dirs:
        if not os.path.isdir(image_dir):
            sys.exit(f"Error: Image directory '{image_dir}' does not exist.")
        build_config_path = os.path.join(image_dir, 'build-config.json')

        config = load_config(build_config_path, default_config)

        image_name = os.path.basename(image_dir)

        base_os_list = config['base_os']
        osg_series_list = config['osg_series']
        base_repo_list = config['base_repo']

        combinations = product(
            base_os_list,
            osg_series_list,
            base_repo_list
        )

        for base_os, osg_series, base_repo in combinations:
        # Constructs a unique configuration string to represent each build setting.
        # This combines the base OS, OSG series, base repository, and two standard
        # build parameters, making it easy to identify and manage each configuration.
        # This approach is preferred because GHA's inability to deal with nested JSON 
        # structures in the matrix construction and it offers:
        # 1. Simplicity: Using a single string to represent configurations is straightforward and easy to understand.
        # 2. Integration: A single string is easily passed to external tools and systems that manage builds.
            configuration_string = f"{base_os}-{osg_series}-{base_repo}-{config['standard_build']}-{config['repo_build']}"
            include_list.append({"name": image_name, "config": configuration_string})

    sys.stdout.flush()
    json_output = json.dumps({"include": include_list}, indent=4)
    print(json_output)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(f"Usage: {sys.argv[0]} <image_dirs>")

    image_dirs = sys.argv[1:]
    main(image_dirs)
