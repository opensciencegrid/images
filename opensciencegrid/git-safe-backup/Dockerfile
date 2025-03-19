# Multiplex a single docker image for the two github backup scripts
# - safe-backup.sh backs up raw git repository content
# - github-metadata-backup.sh backs up github-specific metadata such as issues

FROM almalinux:9

LABEL maintainer="OSG Software <help@osg-htc.org>"

# Mounted directory to output git repositories
ENV TOP_DIR=/data
# Mounted list of remote repositories to back up
ENV REMOTES_LIST=/etc/remotes.list

# from: address for error emails
ENV EMAIL_FROM="example@example.com"

# to: address for error emails
ENV EMAIL_TO="example@example.com"

# Install dependencies
RUN yum install -y git logrotate python3-pip && \
    pip3 install PyGithub

COPY safe-backup.sh send_mail.py github-metadata-backup.sh safe-backup.sh ghb.py /bin/
CMD [ "/bin/safe-backup.sh" ]
