import json
import os
import sys
from itertools import product

def load_config(config_path):
    """Load JSON configuration from the given path."""
    with open(config_path, 'r') as file:
        return json.load(file)

def main(image_dirs):
    print("Image directories:", image_dirs)  # Print the directories

    # Load the default build config
    default_config_path = 'opensciencegrid/default-build-config.json'
    default_config = load_config(default_config_path)

    grouped_configurations = {}

    for image_dir in image_dirs:
        # Check if the image directory exists
        if not os.path.isdir(image_dir):
            sys.exit(f"Error: Image directory '{image_dir}' does not exist.")

        # Construct the path to the build-config.json for the current image
        build_config_path = os.path.join(image_dir, 'build-config.json')

        # Attempt to load the build-config.json file
        try:
            config = load_config(build_config_path)
        except FileNotFoundError:
            config = default_config

        # Get the image name from the directory
        image_name = os.path.basename(image_dir)

        # Initialize the dictionary for this image if not already initialized
        if image_name not in grouped_configurations:
            grouped_configurations[image_name] = []

        # Create all combinations of the parameters
        base_os_list = config['base_os'][0].split(', ')
        osg_series_list = config['osg_series'][0].split(', ')
        base_repo_list = config['base_repo']

        combinations = product(
            base_os_list,
            osg_series_list,
            base_repo_list
        )

        for base_os, osg_series, base_repo in combinations:
            configuration_string = f"{base_os}-{osg_series}-{base_repo}-{config['standard_build']}-{config['repo_build']}"
            grouped_configurations[image_name].append(configuration_string)

    # Output all configurations to a single JSON file in the scripts directory
    output_path = os.path.join('scripts', 'grouped_output.json')
    os.makedirs('scripts', exist_ok=True)
    with open(output_path, 'w') as outfile:
        json.dump(grouped_configurations, outfile, indent=4)
    print(f"Generated {output_path} with grouped image configurations")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(f"Usage: {sys.argv[0]} <image_dirs>")

    image_dirs = sys.argv[1:]
    main(image_dirs)