#!/bin/bash

# Fix permissions for chroma_db
chown -R 1000:1000 /usr/src/app/chroma_db

# Run the main command
exec "$@"