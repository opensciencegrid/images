#!/usr/bin/env python3

import os
import time
import yaml
import datetime
import subprocess
import argparse

start_dir = os.getcwd()

def main():
    parser = argparse.ArgumentParser(
        description='Pull and update container images from Docker to Apptainer/Singularity format'
    )
    parser.add_argument(
        'target_dir',
        help='Target directory where images will be stored'
    )
    parser.add_argument(
        '--config',
        default='images.yaml',
        help='Path to the configuration YAML file (default: images.yaml)'
    )
    parser.add_argument(
        '--keep-days',
        type=int,
        default=10,
        help='Number of days to keep old images (default: 10)'
    )

    args = parser.parse_args()

    with open(args.config) as file:
        conf = yaml.safe_load(file)

    now = datetime.datetime.now(datetime.timezone.utc)
    now_human = now.strftime("%Y-%m-%d %H:%M:%S %Z")
    ts = now.strftime("%Y%m%dT%H%M%SZ")

    print(f"\n[{now_human}]: Starting run for {len(conf)} images\n")

    starttime = time.monotonic()
    for img in conf:

        subprocess.run("apptainer cache clean -f", shell=True)

        archs = img.get("arch", ["x86_64"])
        for arch in archs:
            final_sif = f"{ts}.sif"
            sing_arch = "arm64" if arch == "aarch64" else "amd64"

            os.chdir(start_dir)
            os.makedirs(os.path.join(args.target_dir, arch, img["name"]), exist_ok=True)
            os.chdir(os.path.join(args.target_dir, arch, img["name"]))

            print(f"Working in {os.getcwd()}")

            # log the build to a file in the same structure under logs/
            log_dir = os.path.join("../../..", args.target_dir, "logs", arch)
            os.makedirs(log_dir, exist_ok=True)
            log_file = os.path.join(log_dir, f"{img['name']}.txt")

            cmd = f"apptainer pull --arch {sing_arch} --force --name {final_sif} docker://{img['docker_image']}"
            print(f"Running: {cmd}")
            try:
                with open(log_file, 'w') as f:
                    result = subprocess.run(
                        cmd.split(),
                        stdout=f,
                        stderr=subprocess.STDOUT,
                        text=True,
                        check=True
                    )
            except subprocess.CalledProcessError as e:
                print(f"✗ Failed to pull {img['name']} for {arch} (exit code: {e.returncode}) - check logs")
                continue

            # update latest
            subprocess.run("ls *.sif | sort | tail -n 1 > latest.txt", shell=True)

            # cleanup old images, keep only latest N
            subprocess.run(f"find . -maxdepth 1 -name \\*.sif -mtime +{args.keep_days} -exec rm -f {{}} \\;", shell=True)

    now2 = datetime.datetime.now(datetime.timezone.utc)
    now2_human = now2.strftime("%Y-%m-%d %H:%M:%S %Z")
    endtime = time.monotonic()

    print(f"\n[{now2_human}]: Finished run (elapsed: {datetime.timedelta(seconds=endtime-starttime)!s})\n")


if __name__ == "__main__":
    main()
