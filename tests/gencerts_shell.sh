#!/bin/bash

SUBJ="/C=US/ST=California/L=Santa Clara"
CRT_AUTH="${OPENSSL_SUBJ}/CN=fake-CA"
SERVER="${OPENSSL_SUBJ}/CN=fake-server"
CLIENT="${OPENSSL_SUBJ}/CN=fake-client"

# Create clean environment
cd certs/
rm *.pem

# Create CA certificate
openssl genrsa 2048 > ca-key.pem
openssl req -new -x509 -nodes -days 3600 \
	-subj "${CRT_AUTH}" \
        -key ca-key.pem -out ca.pem

cp ca.pem proxysql-ca.pem

# Create server certificate, remove passphrase, and sign it
# server-cert.pem = public key, server-key.pem = private key
openssl req -newkey rsa:2048 -days 3600 \
        -subj "${SERVER}" \
        -nodes -keyout server-key.pem -out server-req.pem
openssl rsa -in server-key.pem -out server-key.pem
openssl x509 -req -in server-req.pem -days 3600 \
        -CA ca.pem -CAkey ca-key.pem -set_serial 01 -out server-cert.pem
openssl verify -CAfile ca.pem server-cert.pem

cp server-cert.pem proxysql-cert.pem
cp server-key.pem proxysql-key.pem

# Create client certificate, remove passphrase, and sign it
# client-cert.pem = public key, client-key.pem = private key
openssl req -newkey rsa:2048 -days 3600 \
        -subj "${CLIENT}" \
        -nodes -keyout client-key.pem -out client-req.pem
openssl rsa -in client-key.pem -out client-key.pem
openssl x509 -req -in client-req.pem -days 3600 \
        -CA ca.pem -CAkey ca-key.pem -set_serial 01 -out client-cert.pem
# Verify the certificates are correct
openssl verify -CAfile ca.pem client-cert.pem

cd ..
