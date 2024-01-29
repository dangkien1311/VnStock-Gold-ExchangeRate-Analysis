#!/bin/bash

while true; do
    python3 /home/kiendt/code/ETL/extract_mp3.py
    read -n 1 -p "Press 1 to exit, Enter to rerun: " key

    if [ "$key" == "1" ]; then
        exit 0
    fi

    # If any key other than "1" is pressed, continue to the next iteration
done
