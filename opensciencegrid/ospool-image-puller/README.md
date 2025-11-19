# ospool-image-puller

This image periodically pulls images from Docker registries and converts them to SIF files.
The SIF files have timestamped names and each directory has a `latest.txt` file that
points to the latest SIF file in the directory.

This should be run as a sidecar on a webserver or OSDF origin, or standalone but sharing
a volume with a webserver or OSDF origin.

Images will be stored in the volume mounted at `/ospool/images`.

Environment variables:

- CRON_EXPR: cron schedule string (default `30 5 * * *`).
  The time zone is UTC. You can set this to `@reboot` to pull once at startup.

- TIMEOUT: timeout after which the updater will be killed (default "23h").
  If units aren't specified, they will be treated as seconds.

- IMAGES_UID: the UID the files and directories should be written as.
  This UID must have the ability to write to `/ospool/images`.
  A user named `images` will be created with this UID at startup.

To customize the images being pulled, bind-mount a file over
`/ospool/images-scripts/images.yaml`.
