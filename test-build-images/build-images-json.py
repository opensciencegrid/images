import json
import os
import sys

def load_config(config_path):
    """Load JSON configuration from the given path."""
    with open(config_path, 'r') as file:
        return json.load(file)

def main(image_list_file):
    # Load the list of image directories
    with open(image_list_file, 'r') as file:
        image_dirs = json.load(file)

    # Load the default build config
    default_config_path = 'opensciencegrid/default-build-config.json'
    default_config = load_config(default_config_path)

    image_matrix = {}

    for image_dir in image_dirs:
        if image_dir == "dummy":
            continue
        # Construct the path to the build-config.json for the current image
        build_config_path = os.path.join(image_dir, 'build-config.json')

        # Check if the build-config.json file exists, otherwise use the default config
        if os.path.exists(build_config_path):
            config = load_config(build_config_path)
        else:
            config = default_config

        # Get the image name from the directory
        image_name = os.path.basename(image_dir)

        # Add the configuration to the matrix with explicit field handling
        image_matrix[image_name] = {
            "standard_build": config.get("standard_build", False),
            "repo_build": config.get("repo_build", False),
            "base_os": config.get("base_os", []),
            "osg_series": config.get("osg_series", []),
            "base_repo": config.get("base_repo", [])
        }

    # Output the resulting JSON matrix
    print(json.dumps(image_matrix, indent=4))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <image_list_file>")
        sys.exit(1)

    image_list_file = sys.argv[1]
    main(image_list_file)
