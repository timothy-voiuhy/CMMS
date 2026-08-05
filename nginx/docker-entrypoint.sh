#!/bin/sh
set -e

CERT_DIR=/etc/nginx/certs
CERT_FILE="$CERT_DIR/tls.crt"
KEY_FILE="$CERT_DIR/tls.key"

mkdir -p "$CERT_DIR"

if [ ! -f "$CERT_FILE" ] || [ ! -f "$KEY_FILE" ]; then
  if echo "${TLS_CERT_CN:-localhost}" | grep -Eq '^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$'; then
    ALT_NAME="IP:${TLS_CERT_CN:-localhost}"
  else
    ALT_NAME="DNS:${TLS_CERT_CN:-localhost}"
  fi

  openssl req -x509 -nodes -newkey rsa:2048 \
    -keyout "$KEY_FILE" \
    -out "$CERT_FILE" \
    -days "${TLS_SELF_SIGNED_DAYS:-365}" \
    -subj "/CN=${TLS_CERT_CN:-localhost}" \
    -addext "subjectAltName=$ALT_NAME"
fi

exec "$@"
