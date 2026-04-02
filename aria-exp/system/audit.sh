#!/bin/bash

BASE="/home/comanderanch/aria-language-dev/aria-exp"
OUT="$BASE/system/audit.log"

echo "===== FINAL AUDIT START =====" > "$OUT"
date >> "$OUT"

# ------------------------------------------
# DUPLICATES (HASH)
# ------------------------------------------
echo "" >> "$OUT"
echo "---- DUPLICATES (HASH) ----" >> "$OUT"

find "$BASE" -type f ! -path "*/system/*" -exec sha256sum {} + | sort > /tmp/hashes.txt
awk '{print $1}' /tmp/hashes.txt | uniq -d > /tmp/dupes.txt

while read hash; do
    grep "$hash" /tmp/hashes.txt >> "$OUT"
    echo "" >> "$OUT"
done < /tmp/dupes.txt

# ------------------------------------------
# REAL POINTER CHECK (EXCLUDE SYSTEM FILES)
# ------------------------------------------
echo "" >> "$OUT"
echo "---- REAL BROKEN FILE REFERENCES ----" >> "$OUT"

grep -rE "\.pt|\.pth|\.bin" "$BASE" --exclude-dir=system | while read line; do
    path=$(echo "$line" | grep -oE "/home/comanderanch[^ \"']+")
    
    if [ -n "$path" ]; then
        if [ ! -f "$path" ]; then
            echo "BROKEN FILE: $line" >> "$OUT"
        fi
    fi
done

# ------------------------------------------
# DIRECTORY COLLISIONS
# ------------------------------------------
echo "" >> "$OUT"
echo "---- DIRECTORY NAME COLLISIONS ----" >> "$OUT"

find "$BASE" -type d ! -path "*/system/*" -printf "%f\n" | sort | uniq -d >> "$OUT"

# ------------------------------------------
# CHECKPOINT MAP
# ------------------------------------------
echo "" >> "$OUT"
echo "---- CHECKPOINT FILES ----" >> "$OUT"

find "$BASE" -type f \( -name "*.pt" -o -name "*.pth" \) ! -path "*/system/*" >> "$OUT"

# ------------------------------------------
# CLEAN
# ------------------------------------------
rm -f /tmp/hashes.txt /tmp/dupes.txt

echo "" >> "$OUT"
echo "===== FINAL AUDIT COMPLETE =====" >> "$OUT"

echo "AUDIT CLEAN"