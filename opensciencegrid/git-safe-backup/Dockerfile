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
RUN yum install -y git logrotate

COPY safe-backup.sh send_mail.py /bin/
CMD [ "/bin/safe-backup.sh" ]
