#!/bin/bash

# Source environment variables from config.sh if it exists
. $(dirname "$0")/config.sh

# IMPORTANT: Replace with the IP address of PC2
PORT=9999
COUNT=1

echo "Start sending packets continuously to $DISPLAY_ADRESS:$PORT..."
echo "Press Ctrl+C to stop."
echo "---------------------------------------------"

# Infinite loop to send packets
while true; do
  # Create packet content including sequence number and current time
  MESSAGE="Package no $COUNT | Time: $(date)"

  # Print to screen to indicate sent message
  echo "Sending: $MESSAGE"

  # Send packet using nc
  echo "$MESSAGE" | nc $DISPLAY_ADRESS $PORT

  # Increment counter
  COUNT=$((COUNT + 1))

  # Wait 1 second before sending the next packet
  sleep 1
done
