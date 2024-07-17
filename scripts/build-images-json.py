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

    print("Image directories:", image_dirs)  

    # Load the default build config
    default_config_path = 'opensciencegrid/default-build-config.json'
    default_config = load_config(default_config_path)

    image_matrix = {}

    for image_dir in image_dirs:
        if image_dir == "dummy":
            continue

        build_config_path = os.path.join(image_dir, 'build-config.json')

        if os.path.exists(build_config_path):
            config = load_config(build_config_path)
        else:
            config = default_config

        image_name = os.path.basename(image_dir)
        image_matrix[image_name] = config

    output_json = json.dumps(image_matrix, indent=4)
    print(output_json)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <image_list_file>")
        sys.exit(1)

    image_list_file = sys.argv[1]
    main(image_list_file)
