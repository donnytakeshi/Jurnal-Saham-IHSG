#!/usr/bin/env bash
set -euo pipefail

# generate_keystore.sh
# Generates a local release keystore for local testing.
# Usage: ./scripts/generate_keystore.sh [keystore-path] [alias] [storepass] [keypass]

KEYSTORE_PATH=${1:-keystore/release.keystore}
ALIAS=${2:-releasekey}
STOREPASS=${3:-android}
KEYPASS=${4:-android}

mkdir -p "$(dirname "$KEYSTORE_PATH")"

echo "Generating keystore at $KEYSTORE_PATH (alias=$ALIAS)"
keytool -genkeypair -v \
  -keystore "$KEYSTORE_PATH" \
  -alias "$ALIAS" \
  -keyalg RSA -keysize 2048 -validity 10000 \
  -storepass "$STOREPASS" -keypass "$KEYPASS" \
  -dname "CN=Unknown, OU=Unknown, O=Unknown, L=Unknown, S=Unknown, C=US"

echo "Keystore created: $KEYSTORE_PATH"
