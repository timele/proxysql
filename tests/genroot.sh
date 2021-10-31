#!/bin/bash
# Generate new CA certificate root-ca.pem file.

OPENSSL_ROOT_CA=$1

docker run --rm -v $PWD/certs:/certs -it nginx \
    openssl genrsa 2048 > certs/ca-key.pem

docker run --rm -v $PWD/certs:/certs -it nginx \
    openssl req -new -x509 -nodes -days 3600 \
        -subj "${OPENSSL_ROOT_CA}" \
        -key /certs/ca-key.pem -out /certs/ca.pem