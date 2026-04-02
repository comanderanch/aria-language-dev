#!/bin/bash

SRC=$1
DST=$2

BACKUP="$(pwd)/aria-exp/backup_$(date +%s)"

mkdir -p "$BACKUP"

echo "Backing up destination..."
cp -r "$DST" "$BACKUP"

echo "Merging..."
rsync -av --ignore-existing "$SRC"/ "$DST"/

echo "Merge complete"
echo "Backup stored at: $BACKUP"
