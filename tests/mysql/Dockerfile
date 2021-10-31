# We are creating a custom Dockerfile for MySQL as there is no easy way to
# move a file from host into the container. In our case, it's schema.sql
# There is a proposed improvement to "docker cp" but it's still being 
# discussed (https://github.com/docker/docker/issues/5846).
FROM mysql:latest

# allow all traffic for mysqld
RUN echo "mysqld: ALL: allow" >> /etc/hosts.allow 

#####
# Courtesy of https://github.com/Dansyuqri/docker_mysql_ssl
# Create a directory called certs in the image
RUN mkdir -p /etc/certs
# Copy all certs and keys into the newly created /etc/certs
COPY certs/*.pem /etc/certs/
# IMPORTANT: chown the /etc/certs folder so that it belongs to user:group mysql:mysql
RUN chown -R mysql:mysql /etc/certs
#####