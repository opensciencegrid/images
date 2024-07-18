import json
import os
import sys

def load_config(config_path):
    """Load JSON configuration from the given path."""
    with open(config_path, 'r') as file:
        return json.load(file)

def main(image_dirs):
    print("Image directories:", image_dirs)  # Print the directories

    # Load the default build config
    default_config_path = 'opensciencegrid/default-build-config.json'
    default_config = load_config(default_config_path)

    image_matrix = {}

    for image_dir in image_dirs:
        # Construct the path to the build-config.json for the current image
        build_config_path = os.path.join(image_dir, 'build-config.json')

        # Attempt to load the build-config.json file
        try:
            config = load_config(build_config_path)
        except FileNotFoundError:
            config = default_config

        # Get the image name from the directory
        image_name = os.path.basename(image_dir)

        # Add the configuration to the matrix
        image_matrix[image_name] = config

    # Output the resulting JSON matrix
    output_json = json.dumps(image_matrix, indent=4)
    print(output_json)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(f"Usage: {sys.argv[0]} <image_dirs>")

    image_dirs = sys.argv[1:]
    main(image_dirs)