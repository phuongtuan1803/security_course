#!/bin/bash

# Source environment variables from config.sh if it exists
. $(dirname "$0")/config.sh

PORT=9999

echo "Server is listening on port $PORT..."
echo "-------------------------------------"

# Infinite loop to continuously listen for new connections
while true; do
  # nc will listen, print received data, then exit
  # The while loop will restart nc to wait for the next connection
  nc -l -w 1 -p $PORT
done
