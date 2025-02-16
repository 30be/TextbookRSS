#!/bin/bash
# backout.sh - Moves the last line from read_chapters.txt (inside a given directory)
#              to the top of unread_chapters.txt and outputs that line.
# Usage: ./backout.sh <directory>

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <directory>"
    exit 1
fi

DIR="$1"
READ_FILE="$DIR/read_chapters.txt"
UNREAD_FILE="$DIR/unread_chapters.txt"

for file in "$READ_FILE" "$UNREAD_FILE"; do
    [ -f "$file" ] || { echo "Error: $file not found."; exit 1; }
done

# Get and remove the last line from read_chapters.txt.
line=$(tail -n1 "$READ_FILE")
if [ -z "$line" ]; then
    echo "read_chapters.txt is empty, nothing to move."
    exit 0
fi
head -n -1 "$READ_FILE" > "$READ_FILE.tmp" && mv "$READ_FILE.tmp" "$READ_FILE"

# Prepend the line to unread_chapters.txt.
{ echo "$line"; cat "$UNREAD_FILE"; } > "$UNREAD_FILE.tmp" && mv "$UNREAD_FILE.tmp" "$UNREAD_FILE"

echo "Moved line:"
echo "$line"

