"""
Util to output the list of image directories that have changed between origin/main
and the current commit into the `images` and `image_list` gha output vars
"""
import git
from pathlib import Path
import os
import argparse
import json


ORG_DIRS = ['opensciencegrid', 'iris-hep']

parser = argparse.ArgumentParser()
parser.add_argument('--before', help='SHA of the previous commit to compare against')
args = parser.parse_args()


GITHUB_EVENT_NAME = os.environ['GITHUB_EVENT_NAME']
GITHUB_SHA = os.environ['GITHUB_SHA']
GITHUB_REF = os.environ['GITHUB_REF']
GITHUB_BASE_REF = os.environ['GITHUB_BASE_REF']
GITHUB_OUTPUT = os.environ['GITHUB_OUTPUT']


def _image_from_path(path_str: str):
    """
    Extract the image name (eg. osg-htc/frontier-squid) from a file that changed in a subdirectory
    (eg. osg-htc/frontier-squid/build/build.sh)
    """
    return Path(*Path(path_str).parts[:2])

def get_updated_images():
    """
    Get the list of files changed based on the type of event
    kicking off the GHA:
    1. For the main branch, diff the previous state of main vs
       the current commit
    2. For other branches (i.e., on someone's fork), diff main
       vs the current commit
    3. For PRs, diff the base ref vs the current commit
    4. For everything else (e.g., dispatches), build all images
    """

    updated_images: list[str] = []
    repo = git.Repo('.')
    for org_dir in ORG_DIRS:
        if GITHUB_EVENT_NAME in ['pull_request', 'push']:
            base : str = 'origin/main'
            if GITHUB_EVENT_NAME == 'pull_request':
                base = repo.merge_base(f'origin/{GITHUB_BASE_REF}', 'HEAD')[0].hexsha
            elif GITHUB_REF == 'refs/head/main':
                base = args.before
            # TODO there's probably a better way to get the current commit from the github sha
            current_commit = [r for r in repo.iter_commits() if r.hexsha == GITHUB_SHA][0]
            diff_paths = {f"{_image_from_path(d.a_path)}" for d in current_commit.diff(base) if d.a_path.startswith(org_dir)}
            # Only interested in the top two path entries
            updated_images += diff_paths

        else:
            # List all image root dirs. Example value:
            # "opensciencegrid/vo-frontend opensciencegrid/ospool-cm"
            updated_images += [f"{p}" for p in Path(org_dir).iterdir() if p.is_dir()]
    
    return updated_images


def set_image_list_output(updated_images: list[str]):
    """
    Write the list of updated images, in both JSON and space-separated
    """
    with open(GITHUB_OUTPUT, 'a') as github_output:
        github_output.writelines([
            f"images={' '.join(updated_images)}\n",
            f"image_list={json.dumps(updated_images)}\n",
        ])
    
    # Leave a file containing the image list as debug output
    with open('image_list.json', 'w') as image_list:
        image_list.write(json.dumps(updated_images))


if __name__ == '__main__':
    updated_images = get_updated_images()
    set_image_list_output(updated_images)
