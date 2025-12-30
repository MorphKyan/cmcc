#!/bin/bash

# Remove existing files if they exist to ensure fresh generation
rm -f lan_server.key lan_server.csr lan_server.crt

echo "Generating Private Key..."
openssl genrsa -out lan_server.key 2048

echo "Generating CSR..."
openssl req -new -key lan_server.key -out lan_server.csr -subj "//C=CN/ST=Beijing/L=Beijing/O=CMCC/CN=local.morphk.icu"

echo "Generating Certificate..."
openssl x509 -req -in lan_server.csr -CA cmcc_ca.crt -CAkey cmcc_ca.key -CAcreateserial -out lan_server.crt -days 3650 -sha256 -extfile lan_ext.cnf

echo "Done. Created lan_server.key and lan_server.crt"
