#!/bin/bash

# Apply database migrations
alembic upgrade head

# Fix permissions
chown -R 1000:1000 /usr/src/app/chroma_db

# Start the application
exec "$@"